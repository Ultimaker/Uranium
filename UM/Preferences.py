# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser

from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType #To register the MIME type of the preference file.
from UM.SaveFile import SaveFile

MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-preferences",
        comment = "Uranium Preferences File",
        suffixes = ["cfg"],
        preferred_suffix = "cfg"
    )
)

##      Preferences are application based settings that are saved for future use. 
#       Typical preferences would be window size, standard machine, etc.
@signalemitter
class Preferences:
    Version = 5

    def __init__(self):
        super().__init__()

        self._file = None
        self._parser = None
        self._preferences = {}

    def addPreference(self, key, default_value):
        preference = self._findPreference(key)
        if preference:
            preference.setDefault(default_value)
            return

        group, key = self._splitKey(key)
        if group not in self._preferences:
            self._preferences[group] = {}

        self._preferences[group][key] = _Preference(key, default_value)

    ##  Changes the default value of a preference.
    #
    #   If the preference is currently set to the old default, the value of the
    #   preference will be set to the new default.
    #
    #   \param key The key of the preference to set the default of.
    #   \param default_value The new default value of the preference.
    def setDefault(self, key, default_value):
        preference = self._findPreference(key)
        if not preference: #Key not found.
            Logger.log("w", "Tried to set the default value of non-existing setting %s.", key)
            return
        if preference.getValue() == preference.getDefault():
            self.setValue(key, default_value)
        preference.setDefault(default_value)

    def setValue(self, key, value):
        preference = self._findPreference(key)

        if preference:
            preference.setValue(value)
            self.preferenceChanged.emit(key)
        else:
            Logger.log("w", "Tried to set the value of non-existing setting %s.", key)

    def getValue(self, key):
        preference = self._findPreference(key)

        if preference:
            value = preference.getValue()
            if value == "True":
                value = True
            elif value == "False":
                value = False
            return value

        Logger.log("w", "Tried to get the value of non-existing setting %s.", key)
        return None

    def resetPreference(self, key):
        preference = self._findPreference(key)

        if preference:
            preference.setValue(preference.getDefault())
            self.preferenceChanged.emit(key)

    def readFromFile(self, file):
        self._loadFile(file)

        if not self._parser:
            return

        for group, group_entries in self._parser.items():
            if group == "DEFAULT":
                continue

            if group not in self._preferences:
                self._preferences[group] = {}

            for key, value in group_entries.items():
                if key not in self._preferences[group]:
                    self._preferences[group][key] = _Preference(key)

                self._preferences[group][key].setValue(value)
                self.preferenceChanged.emit("{0}/{1}".format(group, key))

    def writeToFile(self, file):
        parser = configparser.ConfigParser(interpolation = None) #pylint: disable=bad-whitespace
        for group, group_entries in self._preferences.items():
            parser[group] = {}
            for key, pref in group_entries.items():
                if pref.getValue() != pref.getDefault():
                    parser[group][key] = str(pref.getValue())

        parser["general"]["version"] = str(Preferences.Version)

        try:
            if hasattr(file, "read"):  # If it already is a stream like object, write right away
                parser.write(file)
            else:
                with SaveFile(file, "wt") as save_file:
                    parser.write(save_file)
        except Exception as e:
            Logger.log("e", "Failed to write preferences to %s: %s", file, str(e))

    preferenceChanged = Signal()

    @classmethod
    def getInstance(cls) -> "Preferences":
        if not cls._instance:
            cls._instance = Preferences()

        return cls._instance

    def _splitKey(self, key):
        group = "general"
        key = key

        if "/" in key:
            parts = key.split("/")
            group = parts[0]
            key = parts[1]

        return (group, key)

    def _findPreference(self, key):
        group, key = self._splitKey(key)

        if group in self._preferences:
            if key in self._preferences[group]:
                return self._preferences[group][key]

        return None

    def _loadFile(self, file):
        if self._file and self._file == file:
            return self._parser
        try:
            self._parser = configparser.ConfigParser(interpolation = None) #pylint: disable=bad-whitespace
            if hasattr(file, "read"):
                self._parser.read_file(file)
            else:
                self._parser.read(file, encoding = "utf-8")

            if self._parser["general"]["version"] != str(Preferences.Version):
                Logger.log("w", "Old config file found, ignoring")
                self._parser = None
                return
        except Exception:
            Logger.logException("e", "An exception occured while trying to read preferences file")
            self._parser = None
            return

        del self._parser["general"]["version"]

    _instance = None    # type: Preferences

class _Preference:
    def __init__(self, name, default = None, value = None): #pylint: disable=bad-whitespace
        self._name = name
        self._default = default
        self._value = default if value is None else value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def getDefault(self):
        return self._default

    def setDefault(self, default):
        self._default = default

    def setValue(self, value):
        self._value = value
