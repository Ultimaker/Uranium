import traceback, sys
class MachineSettings(object):
    def __init__(self):
        self._categories = []
    
    def loadSettingsFromFile(self, file_name):
        pass
    
    def addSettingsCategory(self, category):
        assert(self.getSettingsCategory(category.getKey()) is None)
        self._categories.append(category)
        self._categories.sort()
        
    def getSettingsCategory(self, key):
        for category in self._categories:
            if category.getKey() == key:
                return category
        return None
    
    def getAllCategories(self):
        return self._categories
    
    def getSettingByKey(self, key):
        for category in self._categories:
            setting = category.getSettingByKey(key)
            if setting is not None:
                return setting
        return None #No setting found
   
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

    def setSettingValueByKey(self, key, value):
        setting = self.getSettingByKey(key)
        if setting is not None:
            setting.setValue(value)

    def getSettingValueByKey(self, key):
        setting = self.getSettingByKey(key)
        if setting is not None:
            return setting.getValue()
        traceback.print_stack()
        sys.stderr.write('Setting key not found: %s' % key)
        return None