# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from UM.Signal import Signal, SignalEmitter
from UM.Application import Application

from copy import deepcopy

class SettingOverrideDecorator(SceneNodeDecorator, SignalEmitter):
    def __init__(self):
        super().__init__()

        self._settings = {}

    settingAdded = Signal()
    settingRemoved = Signal()
    settingChanged = Signal()

    def getAllSettings(self):
        return self._settings

    def addSetting(self, key):
        instance = Application.getInstance().getMachineManager().getActiveMachineInstance()

        setting = instance.getSettingByKey(key)
        if not setting:
            return

        setting_clone = deepcopy(setting)
        setting_clone.setParent(None)
        self._settings[key] = setting_clone

        self.settingAdded.emit()

    def setSettingValue(self, key, value):
        if key not in self._settings:
            return

        self._settings[key].setValue(value)
        self.settingChanged.emit(self._settings[key])

    def getSetting(self, key):
        if key not in self._settings:
            parent = self._node.getParent()
            # It could be that the parent does not have a decoration but it's parent parent does. 
            while parent is not None:
                if parent.hasDecoration("getSetting"):
                    return parent.callDecoration("getSetting")
                else:
                    parent = parent.getParent()
        else:
            return self._settings[key]

    def removeSetting(self, key):
        if key not in self._settings:
            return

        del self._settings[key]
        self.settingRemoved.emit()
