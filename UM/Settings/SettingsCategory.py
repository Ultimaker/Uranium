# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Settings.Setting import Setting
from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger

##  A Category containing a bunch of settings.
class SettingsCategory(SignalEmitter):
    def __init__(self, machine_manager, key, catalog, parent, icon = None, order = 0):
        self._key = key
        self._i18n_catalog = catalog
        self._label = key
        self._parent = parent
        self._tooltip = ""
        self._icon = icon if icon else "category_unknown"
        self._order = order
        self._visible = True
        self._children_visible = False
        self._settings = []
        self._depth = 0 #Depth of category is 0 by definition (used for display purposes)
        self._machine_manager = machine_manager
        
    ##  Set values of the setting by providing it with a dict object (as decoded by JSON parser)
    #   \param data Decoded JSON dict
    def fillByDict(self, data):
        if "label" in data:
            self._label = self._i18n_catalog.i18nc("{0} label".format(self._key), data["label"])
        if "visible" in data:
            self._visible = data["visible"]
        if "icon" in data:
            self._icon = data["icon"]
        if "settings" in data:
            for key, value in data["settings"].items():
                setting = self.getSetting(key)
                if not setting:
                    if "default" not in value and "type" not in value:
                        Logger.log("w", "Invalid setting definition for setting %s", key)
                        continue

                    setting = Setting(self._machine_manager, key, self._i18n_catalog, type = value["type"])
                    setting.setCategory(self)
                    setting.setParent(self)
                    self._settings.append(setting)

                setting.fillByDict(value)
                setting.visibleChanged.connect(self._onSettingVisibleChanged)
                setting.defaultValueChanged.connect(self.defaultValueChanged)

        self._onSettingVisibleChanged(None)

    def isActive(self):
        return True
    
    def setLabel(self, label):
        self._label = label
    
    def getDepth(self):
        return self._depth

    def setVisible(self, visible):
        if visible != self._visible:
            self._visible = visible
            self.visibleChanged.emit()

    def isVisible(self):
        if self._visible:
            return self._children_visible or self.getHiddenValuesCount() != 0

        return False

    visibleChanged = Signal()

    defaultValueChanged = Signal()

    ##  Get the number of settings in this category that are not visible and have a custom value set.
    def getHiddenValuesCount(self):
        count = 0
        if self._machine_manager.getWorkingProfile():
            for setting in self.getAllSettings():
                if not setting.isVisible() and self._machine_manager.getWorkingProfile().hasSettingValue(setting.getKey(), filter_defaults = False):
                    count += 1

        return count

    def addSetting(self, setting):
        self._settings.append(setting)

    def getSetting(self, key):
        for s in self._settings:
            ret = s.getSetting(key)
            if ret is not None:
                return ret
        return None # No setting was found

    def getLabel(self):
        return self._label

    def getKey(self):
        return self._key

    def getIcon(self):
        return self._icon

    def getParent(self):
        return self._parent

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
        return "<SettingCategory: %s %d>" % (self._key, self._order)

    def _onSettingVisibleChanged(self, setting):
        for setting in self.getAllSettings():
            if setting.isVisible():
                self._children_visible = True
                break
        else:
            self._children_visible = False

        self.visibleChanged.emit(self)
