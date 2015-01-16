import traceback, sys
import json
import configparser
import os.path

from UM.Settings.SettingsCategory import SettingsCategory
from UM.Signal import Signal, SignalEmitter
from PyQt5.QtCore import QCoreApplication
from UM.Logger import Logger

class MachineSettings(object):
    def __init__(self):
        self._categories = []
        self._platformMesh = None
    
    ##  Load settings from JSON file. Used to load tree structure & default values etc from file.
    #   /param file_name String 
    def loadSettingsFromFile(self, file_name):
        json_data = open(file_name)
        data = json.load(json_data)
        json_data.close()

        if "platform" in data:
            self._platformMesh = data["platform"]

        if "Categories" in data:
            for category in data["Categories"]:
                if "key" in category:
                    temp_category = SettingsCategory(category["key"])
                    temp_category.fillByDict(category)
                    self.addSettingsCategory(temp_category)
        self.settingsLoaded.emit() #Emit signal that all settings are loaded (some setting stuff can only be done when all settings are loaded (eg; the conditional stuff)
    
    settingsLoaded = Signal()
    
    ##  Load values of settings from file. 
    def loadValuesFromFile(self, file_name):
        config = configparser.ConfigParser()
        config.read(file_name)

        for name, section in config.items():
            for key in section:
                setting = self.getSettingByKey(key)

                if setting is not None:
                    setting.setValue(section[key])
    
    ##  Save setting values to file
    def saveValuesToFile(self, file_name):
        config = configparser.ConfigParser()

        for category in self._categories:
            configData = {}
            for setting in category.getAllSettings():
                if setting.isVisible():
                    configData[setting.getKey()] = setting.getValue()
            config[category.getKey()] = configData

        with open(file_name, 'w') as f:
            config.write(f)
        
    ##  Add a category of settings
    def addSettingsCategory(self, category):
        self._categories.append(category)
    
    ##  Get setting category by key
    #   \param key Category key to get.
    #   \return category or None if key was not found.
    def getSettingsCategory(self, key):
        for category in self._categories:
            if category.getKey() == key:
                return category
        return None
    
    ##  Get all categories.
    #   \returns list of categories
    def getAllCategories(self):
        return self._categories
    
    ##  Get all settings of this machine
    #   \return list of settings
    def getAllSettings(self):
        all_settings = []
        for category in self._categories:
            all_settings.extend(category.getAllSettings())
        return all_settings
    
    ##  Get setting by key.
    #   \param key Key to select setting by (string)
    #   \return Setting or none if no setting was found.
    def getSettingByKey(self, key):
        for category in self._categories:
            setting = category.getSettingByKey(key)
            if setting is not None:
                return setting
        return None #No setting found
   
    ##  Add setting to machine.
    #   \param parent_key Key of the category that the seting needs to be added to
    #   \param setting Setting to add.
    def addSetting(self, parent_key, setting):
        setting.setMachine(self)        
        category = self.getSettingsCategory(parent_key)
        if category is not None:
            category.addSetting(setting)
            setting.setCategory(category)
            return
        
        setting_parent = self.getSettingByKey(parent_key)
        if setting_parent is not None:
            setting_parent.addSetting(setting)
            setting.setCategory(setting_parent.getCategory())
            return
    
    ##  Set the value of a setting by key.
    #   \param key Key of setting to change.
    #   \param value value to set.
    def setSettingValueByKey(self, key, value):
        setting = self.getSettingByKey(key)
        if setting is not None:
            setting.setValue(value)
   
    ##  Get the value of setting by key.
    #   \param key Key of the setting to get value from
    #   \return value (or none)
    def getSettingValueByKey(self, key):
        setting = self.getSettingByKey(key)
        if setting is not None:
            return setting.getValue()
        Logger.log('e', "Could not find setting %s, unable to read the value" % (data_id))
        return None
    
    ##  Get the machine mesh (in most cases platform)
    #   Todo: Might need to rename this to get machine mesh?
    def getPlatformMesh(self):
        return self._platformMesh
