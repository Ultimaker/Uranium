from UM.Settings.Setting import Setting
class SettingsCategory(object):
    def __init__(self, key, icon = None, order = 0):
        self._key = key
        self._label = key
        self._tooltip = ''
        self._icon = icon
        self._order = order
        self._visible = True
        self._settings = []
        self._depth = 0 #Depth of category is 0 by definition (used for display purposes)
        
    ## Set values of the setting by providing it with a dict object (as decoded by JSON parser)
    # \param data Decoded JSON dict
    def fillByDict(self, data):
        if "label" in data:
            self._label = data["label"]
        if "visible" in data:
            self._visible = data["visible"]
        if "Settings" in data:
            for setting in data["Settings"]:
                if "key" in setting and "default" in setting and "type" in setting:
                    temp_setting = Setting(setting["key"],setting["default"],setting["type"])
                    temp_setting.fillByDict(setting)
                    temp_setting.setCategory(self)
                    temp_setting.setParent(self)
                    self._settings.append(temp_setting)

    def setLabel(self, label):
        self._label = label
    
    def getDepth(self):
        return self._depth
    
    def setVisible(self, visible):
        self._visible = visible

    def isVisible(self):
        return self._visible

    def addSetting(self, setting):
        self._settings.append(setting)

    def getSettingByKey(self, key):
        for s in self._settings:
            ret = s.getSettingByKey(key)
            if ret is not None:
                return ret
        return None # No setting was found

    def getLabel(self):
        return self._label

    def getKey(self):
        return self._key

    def getIcon(self):
        return self._icon

    def __cmp__(self, other):
        return self._order - other._order

    def getAllSettings(self):
        all_settings = []
        for s in self._settings:
            all_settings.append(s)
            all_settings.extend(s.getAllChildren())
        return all_settings

    def getChildren(self):
        return self._settings

    def __repr__(self):
        return '<SettingCategory: %s %d>' % (self._key, self._order)
