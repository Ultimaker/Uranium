# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.
import configparser
class Profile():
    def __init__(self):
        super().__init__()
        self._changed_settings = {}
        
    def setSettingValue(self, key, value):
        self._changed_settings[key] = value
        
    def getSettingValue(self, key):
        try:
            return self._changed_settings[key]
        except:
            return None
    
    def getChangedSettings(self):
        return self._changed_settings
    
    def readFromFile(self, file):
        parser = configparser.ConfigParser()
        parser.read(file)
        if not parser.has_section("General"):
            raise SettingsError.InvalidFileError(path)

        if not parser.has_option("General", "version") or parser.get("General", "version") != self.ProfileVersion:
            raise SettingsError.InvalidVersionError(path)
        for group in parser:
            if group == "DEFAULT":
                continue
            if group == "settings":
                for key, value in parser[group].items():
                    self.setSettingValue(key, value)
    
    def writeToFile(self, file):
        parser = configparser.ConfigParser()
        parser.add_section("settings")
        for setting_key in self._changed_settings:
            parser.set("settings", setting_key , str(self._changed_settings[setting_key]))
            #parser[setting_key] = self._changed_settings[setting_key])
        
        with open(file, "wt") as f:
            parser.write(f)