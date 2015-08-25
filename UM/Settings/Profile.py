# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser

from UM.Signal import Signal, SignalEmitter
from UM.Settings import SettingsError

class Profile(SignalEmitter):
    ProfileVersion = 1

    def __init__(self):
        super().__init__()
        self._changed_settings = {}
        self._name = "Unknown Profile"

    nameChanged = Signal()

    def getName(self):
        return self._name

    def setName(self, name):
        if name != self._name:
            self._name = name
            self.nameChanged.emit()

    def setSettingValue(self, key, value):
        self._changed_settings[key] = value
        
    def getSettingValue(self, key):
        try:
            return self._changed_settings[key]
        except:
            return None
    
    def getChangedSettings(self):
        return self._changed_settings
    
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
