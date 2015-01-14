from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from UM.Qt.ListModel import ListModel
from UM.Settings.Setting import Setting

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
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_settings = QCoreApplication.instance().getMachineSettings()
        self._updateSettings()

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
               
    def _updateSettings(self):
        self.clear()
        settings = self._machine_settings.getAllSettings()
        for setting in settings:
            self.appendItem({"name":setting.getLabel(),"category":setting.getCategory().getLabel(),"collapsed":True,"type":setting.getType(),"value":setting.getValue(),"valid":setting.validate(),"key":setting.getKey(), "depth":setting.getDepth(),"visibility":setting.isVisible(),"disabled":setting.checkAllChildrenVisible(), "options": self.createOptionsModel(setting.getOptions())})
            if setting._active_if_setting != None:
                setting.activeChanged.connect(self.handleActiveChanged)
    
    ##  Triggred by setting if it has a conditional activation
    def handleActiveChanged(self,key):
        temp_setting = self._machine_settings.getSettingByKey(key)
        if temp_setting is not None:
            index = self._find(self.items,"key",temp_setting.getKey())
            if index != -1:
                self.setProperty(index, 'disabled', temp_setting.checkAllChildrenVisible())
                self.setProperty(index, 'visibility', (temp_setting.isVisible() and temp_setting.isActive()))
            
            for child_setting in temp_setting.getAllChildren():
                index = self._find(self.items,"key",child_setting.getKey())
                if index != -1:
                    self.setProperty(index, 'disabled', child_setting.checkAllChildrenVisible())
                    self.setProperty(index, 'visibility', (child_setting.isVisible() and child_setting.isActive()))
            
            

    #   Convenience function that finds the index in a list of dicts based on key value pair
    def _find(self,lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    @pyqtSlot(str)
    def toggleCollapsedByCategory(self, category_key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if item["category"] == category_key:
                self.setProperty(index, 'collapsed', not item['collapsed'])
    
    @pyqtSlot(int, str, str)
    def settingChanged(self, index, key, value):
        #index = self.items.index(key)
        if self._machine_settings.getSettingByKey(key) is not None:
            self._machine_settings.getSettingByKey(key).setValue(value)
        self.setProperty(index,'valid', self.isValid(key))
    
    @pyqtSlot(str,result=int)
    def isValid(self,key):
        if self._machine_settings.getSettingByKey(key) is not None:
            return self._machine_settings.getSettingByKey(key).validate()
        return 5
    
    def createOptionsModel(self, options):
        model = ListModel()
        model.addRoleName(self.NameRole,"text")
        for option in options:
            model.appendItem({"text":str(option)})
        return model    
    
    @pyqtSlot()
    def saveSettingValues(self):
        self._machine_settings.saveValuesToFile("settings.ini")
    
    @pyqtSlot(str,bool)
    def setVisibility(self, key, visibility):
        setting = self._machine_settings.getSettingByKey(key)
        if setting is not None:
            setting.setVisible(visibility)
        
        for index in range(0,len(self.items)):
            temp_setting = self._machine_settings.getSettingByKey(self.items[index]["key"])
            if temp_setting is not None:
                self.setProperty(index, 'disabled', temp_setting.checkAllChildrenVisible())
                self.setProperty(index, 'visibility', temp_setting.isVisible())
                
                
    @pyqtSlot(str,result=bool)
    def checkVisibilityCategory(self,key):
        category = self._machine_settings.getSettingsCategory(key)
        if category is not None:
            for setting in category.getAllSettings():
                if setting.checkAllChildrenVisible() or setting.isVisible:
                    return True
        return False
            
        
        
        