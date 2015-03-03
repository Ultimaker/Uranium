from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Settings.Setting import Setting
from UM.Resources import Resources
from UM.Application import Application

class SettingsModel(ListModel):
    
    NameRole = Qt.UserRole + 1 #Label 
    CategoryRole =Qt.UserRole + 2 #Key of category
    CollapsedRole = Qt.UserRole + 3 #Is it collapsed
    TypeRole = Qt.UserRole + 4 # Type of setting (int, float, string, etc)
    ValueRole = Qt.UserRole + 5 # Value of setting
    ValidRole = Qt.UserRole + 6 # Is value valid (5 = correct, 0-4 is error/warning)
    KeyRole = Qt.UserRole + 7 #Unique identifier of setting
    DepthRole = Qt.UserRole + 8
    VisibilityRole = Qt.UserRole + 9
    DisabledRole = Qt.UserRole + 10
    OptionsRole = Qt.UserRole + 11
    UnitRole = Qt.UserRole + 12
    DescriptionRole = Qt.UserRole + 13
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_settings = None
        Application.getInstance().activeMachineChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.CategoryRole,"category")
        self.addRoleName(self.CollapsedRole,"collapsed")
        self.addRoleName(self.TypeRole,"type")
        self.addRoleName(self.ValueRole,"value") 
        self.addRoleName(self.ValidRole,"valid")
        self.addRoleName(self.KeyRole,"key") 
        self.addRoleName(self.DepthRole,"depth")
        self.addRoleName(self.VisibilityRole,"visibility")
        self.addRoleName(self.DisabledRole,"disabled")
        self.addRoleName(self.OptionsRole,"options")
        self.addRoleName(self.UnitRole,"unit")
        self.addRoleName(self.DescriptionRole, "description")

    ##  Triggred by setting if it has a conditional activation
    def handleActiveChanged(self, key):
        temp_setting = self._machine_settings.getSettingByKey(key)
        if temp_setting is not None:
            index = self._find(self.items,"key",temp_setting.getKey())
            if index != -1:
                self.setProperty(index, 'disabled', (temp_setting.checkAllChildrenVisible() or not temp_setting.isActive())) 
                self.setProperty(index, 'visibility', (temp_setting.isVisible() and temp_setting.isActive()))

            for child_setting in temp_setting.getAllChildren():
                index = self._find(self.items,"key",child_setting.getKey())
                if index != -1:
                    self.setProperty(index, 'disabled', (child_setting.checkAllChildrenVisible() or not child_setting.isActive()))
                    self.setProperty(index, 'visibility', (child_setting.isVisible() and child_setting.isActive()))

    @pyqtSlot(str)
    ##  collapse an entire category
    def toggleCollapsedByCategory(self, category_key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if item["category"] == category_key:
                self.setProperty(index, 'collapsed', not item['collapsed'])

    @pyqtSlot(int, str, str)
    ##  Notification that setting has changed.  
    def settingChanged(self, index, key, value):
        if self._machine_settings.getSettingByKey(key) is not None:
            self._machine_settings.getSettingByKey(key).setValue(value)
        self.setProperty(index,'valid', self.isValid(key))

    @pyqtSlot(str,result=int)
    ##  Check if the entered value of the setting is valid (warning/error)
    #   \returns error key.
    def isValid(self,key):
        if self._machine_settings.getSettingByKey(key) is not None:
            return self._machine_settings.getSettingByKey(key).validate()
        return 5

    ##  Create model for combo box (used by enum type setting) 
    #   \param options List of strings
    #   \return ListModel with "text":value pairs
    def createOptionsModel(self, options):
        model = ListModel()
        model.addRoleName(self.NameRole,"text")
        for option in options:
            model.appendItem({"text":str(option)})
        return model    

    @pyqtSlot()
    ##  Save the current setting values to file.
    def saveSettingValues(self):
        self._machine_settings.saveValuesToFile(Resources.getStoragePath(Resources.SettingsLocation, 'settings.cfg'))

    @pyqtSlot(str,bool)
    ##  Set the visibility of a setting.
    #   Note that this might or might not effect the disabled property aswel!
    #   \param key Key of the setting that is affected
    #   \param visibility Visibility of the setting.
    def setVisibility(self, key, visibility):
        setting = self._machine_settings.getSettingByKey(key)
        if setting is not None:
            setting.setVisible(visibility)

        for index in range(0,len(self.items)):
            temp_setting = self._machine_settings.getSettingByKey(self.items[index]["key"])
            if temp_setting is not None:
                self.setProperty(index, 'disabled', temp_setting.checkAllChildrenVisible())
                self.setProperty(index, 'visibility', temp_setting.isVisible())
                self.setProperty(index, 'value', temp_setting.getValue())

    @pyqtSlot(str,result=bool)
    ##  Check the visibility of an category.
    #   It's possible that all children settings are invisible, so there is no need to show the category.
    #   \param key key of the category to check
    #   \return bool 
    def checkVisibilityCategory(self,key):
        for category in self._machine_settings.getAllCategories():    
            if category.getLabel() == key:
                for setting in category.getAllSettings():
                    if setting.checkAllChildrenVisible() or setting.isVisible():
                        return True
        return False

    #   Convenience function that finds the index in a list of dicts based on key value pair
    def _find(self,lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    def _onActiveMachineChanged(self):
        self.clear()
        if self._machine_settings:
            for setting in self._machine_settings.getAllSettings():
                setting.activeChanged.disconnect(self.handleActiveChanged)

        self._machine_settings = Application.getInstance().getActiveMachine()

        if self._machine_settings:
            for setting in self._machine_settings.getAllSettings():
                self.appendItem({
                    "name": setting.getLabel(),
                    "description": setting.getDescription(),
                    "category": setting.getCategory().getLabel(),
                    "collapsed": True,
                    "type": setting.getType(),
                    "value": setting.getValue(),
                    "valid": setting.validate(),
                    "key": setting.getKey(),
                    "depth": setting.getDepth(),
                    "visibility": (setting.isVisible() and setting.isActive()),
                    "disabled": (setting.checkAllChildrenVisible() or not setting.isActive()),
                    "options": self.createOptionsModel(setting.getOptions()),
                    "unit": setting.getUnit()
                })
                setting.activeChanged.connect(self.handleActiveChanged)
