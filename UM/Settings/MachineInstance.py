# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser

from UM.Settings import SettingsError
from UM.Logger import Logger
from UM.Signal import Signal, SignalEmitter

class MachineInstance(SignalEmitter):
    MachineInstanceVersion = 1

    def __init__(self, machine_manager, **kwargs):
        super().__init__()

        self._machine_manager = machine_manager

        self._name = kwargs.get("name", "")
        self._machine_definition = kwargs.get("definition", None)
        if self._machine_definition:
            self._machine_definition.loadAll()
        self._machine_setting_overrides = {}

    nameChanged = Signal()

    def getName(self):
        return self._name

    def setName(self, name):
        if name != self._name:
            old_name = self._name
            self._name = name
            self.nameChanged.emit(self, old_name)

    def getMachineDefinition(self):
        return self._machine_definition

    def setMachineDefinition(self, definition):
        if not definition:
            return

        definition.loadAll()
        self._machine_definition = definition

    def setMachineSettingValue(self, setting, value):
        if not self._machine_definition.isMachineSetting(setting):
            Logger.log("w", "Tried to override setting %s that is not a machine setting", setting)
            return

        self._machine_setting_overrides[setting] = value

    def getMachineSettingValue(self, setting):
        if not self._machine_definition.isMachineSetting(setting):
            return

        if setting in self._machine_setting_overrides:
            return self._machine_setting_overrides[setting]

        return self._machine_definition.getSetting(setting).getDefaultValue()

    def getSettingValue(self, key):
        if not self._machine_definition.isSetting(key):
            return None

        if key in self._machine_setting_overrides:
            return self._machine_setting_overrides[key]

        return self._machine_definition.getSetting(key).getDefaultValue()

    def hasMachineSettingValue(self, key):
        return key in self._machine_setting_overrides

    def loadFromFile(self, path):
        config = configparser.ConfigParser()
        config.read(path, "utf-8")

        if not config.has_section("general"):
            raise SettingsError.InvalidFileError(path)

        if not config.has_option("general", "version"):
            raise SettingsError.InvalidFileError(path)

        if not config.has_option("general", "name") or not config.has_option("general", "type"):
            raise SettingsError.InvalidFileError(path)

        if int(config.get("general", "version")) != self.MachineInstanceVersion:
            raise SettingsError.InvalidVersionError(path)

        type_name = config.get("general", "type")
        variant_name = config.get("general", "variant", fallback = "")

        self._machine_definition = self._machine_manager.findMachineDefinition(type_name, variant_name)
        self._machine_definition.loadAll()

        self._name = config.get("general", "name")

        for key, value in config["machine_settings"].items():
            self._machine_setting_overrides[key] = value

    def saveToFile(self, path):
        config = configparser.ConfigParser()

        config.add_section("general")
        config["general"]["name"] = self._name
        config["general"]["type"] = self._machine_definition.getId()
        config["general"]["version"] = str(self.MachineInstanceVersion)
        if self._machine_definition.getVariantName():
            config["general"]["variant"] = self._machine_definition.getVariantName()

        config.add_section("machine_settings")
        for key, value in self._machine_setting_overrides:
            config["machine_settings"][key] = str(value)

        with open(path, "wt", -1, "utf-8") as f:
            config.write(f)
