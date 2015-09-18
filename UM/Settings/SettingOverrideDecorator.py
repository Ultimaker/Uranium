# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from UM.Signal import Signal, SignalEmitter
from UM.Application import Application

from copy import deepcopy

##  A decorator that can be used to override individual setting values.
class SettingOverrideDecorator(SceneNodeDecorator, SignalEmitter):
    def __init__(self):
        super().__init__()

        self._settings = {}
        self._setting_values = {}

    settingAdded = Signal()
    settingRemoved = Signal()
    settingValueChanged = Signal()

    def getAllSettings(self):
        return self._settings

    def getAllSettingValues(self):
        values = {}

        for key, setting in self._settings.items():
            if key in self._setting_values:
                values[key] = setting.parseValue(self._setting_values[key])
            else:
                values[key] = setting.getDefaultValue(self)

            for child in setting.getAllChildren():
                child_key = child.getKey()
                if child_key in self._setting_values:
                    values[child_key] = child.parseValue(self._setting_values[child_key])
                else:
                    values[child_key] = child.getDefaultValue(self)

        return values

    def addSetting(self, key):
        instance = Application.getInstance().getMachineManager().getActiveMachineInstance()

        setting = instance.getMachineDefinition().getSetting(key)
        if not setting:
            return

        self._settings[key] = setting

        self.settingAdded.emit()
        Application.getInstance().getController().getScene().sceneChanged.emit(self.getNode())

    def setSettingValue(self, key, value):
        if key not in self._settings:
            return

        self._setting_values[key] = value
        self.settingValueChanged.emit(self._settings[key])
        Application.getInstance().getController().getScene().sceneChanged.emit(self.getNode())

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

    def getSettingValue(self, key):
        if key not in self._settings:
            return Application.getInstance().getMachineManager().getActiveProfile().getSettingValue(key)

        setting = self._settings[key]

        if key in self._setting_values:
            return setting.parseValue(self._setting_values[key])

        return setting.getDefaultValue(self)

    def removeSetting(self, key):
        if key not in self._settings:
            return

        del self._settings[key]

        if key in self._setting_values:
            del self._setting_values[key]

        self.settingRemoved.emit()
        Application.getInstance().getController().getScene().sceneChanged.emit(self.getNode())
