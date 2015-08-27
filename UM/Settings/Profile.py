# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser

from UM.Signal import Signal, SignalEmitter
from UM.Settings import SettingsError
from UM.Logger import Logger

class Profile(SignalEmitter):
    ProfileVersion = 1

    def __init__(self, machine_manager):
        super().__init__()
        self._machine_manager = machine_manager
        self._changed_settings = {}
        self._name = "Unknown Profile"

        self._active_instance = None
        self._machine_manager.activeMachineInstanceChanged.connect(self._onActiveInstanceChanged)
        self._onActiveInstanceChanged()

    nameChanged = Signal()

    def getName(self):
        return self._name

    def setName(self, name):
        if name != self._name:
            self._name = name
            self.nameChanged.emit()

    settingValueChanged = Signal()

    def setSettingValue(self, key, value):
        if not self._active_instance or not self._active_instance.getMachineDefinition().isUserSetting(key):
            Logger.log("w", "Tried to set value of non-user setting %s", key)
            return

        if key in self._changed_settings and self._changed_settings[key] == value:
            return

        self._changed_settings[key] = value
        self.settingValueChanged.emit(key)
        
    def getSettingValue(self, key):
        if not self._active_instance or not self._active_instance.getMachineDefinition().isSetting(key):
            return None

        if key in self._changed_settings:
            return self._changed_settings[key]

        return self._active_instance.getSettingValue(key)

    def getChangedSettings(self):
        return self._changed_settings

    def getAllSettingValues(self, **kwargs):
        values = { }

        if not self._active_instance:
            return values

        settings = self._active_instance.getMachineDefinition().getAllSettings(include_machine = kwargs.get("include_machine", False))

        for setting in settings:
            key = setting.getKey()

            if key in self._changed_settings:
                values[key] = self._changed_settings[key]
                continue

            if self._active_instance.hasMachineSettingValue(key):
                values[key] = self._active_instance.getMachineSettingValue(key)

            values[key] = setting.getDefaultValue()

        return values

    def loadFromFile(self, path):
        parser = configparser.ConfigParser()
        parser.read(path)

        if not parser.has_section("General"):
            raise SettingsError.InvalidFileError(path)

        if not parser.has_option("General", "version") or int(parser.get("General", "version")) != self.ProfileVersion:
            raise SettingsError.InvalidVersionError(path)

        self._name = parser.get("General", "name")

        for group in parser:
            if group == "DEFAULT":
                continue
            if group == "Settings":
                for key, value in parser[group].items():
                    self.setSettingValue(key, value)
    
    def saveToFile(self, file):
        parser = configparser.ConfigParser()

        parser.add_section("General")
        parser.set("General", "version", str(self.ProfileVersion))
        parser.set("General", "name", self._name)

        parser.add_section("Settings")
        for setting_key in self._changed_settings:
            parser.set("Settings", setting_key , str(self._changed_settings[setting_key]))
        
        with open(file, "wt", -1, "utf-8") as f:
            parser.write(f)

    def _onActiveInstanceChanged(self):
        self._active_instance = self._machine_manager.getActiveMachineInstance()
