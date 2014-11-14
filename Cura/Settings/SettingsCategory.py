class SettingsCategory(object):
    def __init__(self, key, icon = None, order = 0):
        self._key = key
        self._label = key
        self._tooltip = ''
        self._icon = icon
        self._order = order
        self._visible = True
        self._settings = []

    def setLabel(self, label):
        self._label = label

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
            all_settings.extend(s)
            all_settings.extend(s.getAllSettings())
        return all_settings

    def getChildren(self):
        return self._settings

    def __repr__(self):
        return '<SettingCategory: %s %d>' % (self._key, self._order)
