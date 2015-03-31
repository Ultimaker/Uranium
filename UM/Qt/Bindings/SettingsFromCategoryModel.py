from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Settings.Setting import Setting
from UM.Resources import Resources
from UM.Application import Application

class SettingsFromCategoryModel(ListModel):
    NameRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    ValueRole = Qt.UserRole + 3
    ValidRole = Qt.UserRole + 4
    KeyRole = Qt.UserRole + 5
    OptionsRole = Qt.UserRole + 6
    UnitRole = Qt.UserRole + 7
    DescriptionRole = Qt.UserRole + 8
    
    def __init__(self, category, parent = None):
        super().__init__(parent)
        self._category = category
        self._updateSettings()

        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.TypeRole,"type")
        self.addRoleName(self.ValueRole,"value") 
        self.addRoleName(self.ValidRole,"valid")
        self.addRoleName(self.KeyRole,"key")
        self.addRoleName(self.OptionsRole,"options")
        self.addRoleName(self.UnitRole,"unit")
        self.addRoleName(self.DescriptionRole, "description")

    ##  Triggred by setting if it has a conditional activation
    #def handleActiveChanged(self, key):
        #temp_setting = self._machine_settings.getSettingByKey(key)
        #if temp_setting is not None:
            #index = self._find(self.items,"key",temp_setting.getKey())
            #if index != -1:
                #self.setProperty(index, 'disabled', (temp_setting.checkAllChildrenVisible() or not temp_setting.isActive()))
                #self.setProperty(index, 'visibility', (temp_setting.isVisible() and temp_setting.isActive()))

            #for child_setting in temp_setting.getAllChildren():
                #index = self._find(self.items,"key",child_setting.getKey())
                #if index != -1:
                    #self.setProperty(index, 'disabled', (child_setting.checkAllChildrenVisible() or not child_setting.isActive()))
                    #self.setProperty(index, 'visibility', (child_setting.isVisible() and child_setting.isActive()))

    @pyqtSlot(int, str, str)
    ##  Notification that setting has changed.  
    def setSettingValue(self, index, key, value):
        if self._category.getSettingByKey(key) is not None:
            self._category.getSettingByKey(key).setValue(value)
        self.setProperty(index,'valid', self.isValid(key))

    @pyqtSlot(str,result=int)
    ##  Check if the entered value of the setting is valid (warning/error)
    #   \returns error key.
    def isValid(self,key):
        if self._category.getSettingByKey(key) is not None:
            return self._category.getSettingByKey(key).validate()
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

    #   Convenience function that finds the index in a list of dicts based on key value pair
    def _find(self,lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    def _updateSettings(self):
        for setting in self._category.getAllSettings():
            if setting.isVisible() and setting.isActive():
                self.appendItem({
                    "name": setting.getLabel(),
                    "description": setting.getDescription(),
                    "type": setting.getType(),
                    "value": setting.getValue(),
                    "valid": setting.validate(),
                    "key": setting.getKey(),
                    "options": self.createOptionsModel(setting.getOptions()),
                    "unit": setting.getUnit()
                })
            #setting.visibleChanged.connect(self._onSettingVisibleChanged)
                #setting.activeChanged.connect(self.handleActiveChanged)
