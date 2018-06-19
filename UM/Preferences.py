# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser
from typing import Any, Dict, IO, Optional, Tuple, Union

from UM.Logging.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType
from UM.SaveFile import SaveFile


MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-preferences",
        comment = "Uranium Preferences File",
        suffixes = ["cfg"],
        preferred_suffix = "cfg"
    )
)


class Preferences:
    Version = 6

    def __init__(self) -> None:
        super().__init__()

        self._parser = None  # type: Optional[configparser.ConfigParser]
        self._preferences = {}  # type: Dict[str, Any]

    def addPreference(self, key: str, default_value: Any) -> None:
        preference = self._findPreference(key)
        if preference:
            preference.setDefault(default_value)
            return

        group, key = self._splitKey(key)
        if group not in self._preferences:
            self._preferences[group] = {}

        self._preferences[group][key] = _Preference(key, default_value)

    def removePreference(self, key: str) -> None:
        preference = self._findPreference(key)
        if preference is None:
            Logger.log("i", "Preferences '%s' doesn't exist, nothing to remove.", key)
            return

        group, key = self._splitKey(key)
        del self._preferences[group][key]
        Logger.log("i", "Preferences '%s' removed.", key)

    ##  Changes the default value of a preference.
    #
    #   If the preference is currently set to the old default, the value of the
    #   preference will be set to the new default.
    #
    #   \param key The key of the preference to set the default of.
    #   \param default_value The new default value of the preference.
    def setDefault(self, key: str, default_value: Any) -> None:
        preference = self._findPreference(key)
        if not preference:
            Logger.log("w", "Tried to set the default value of non-existing setting %s.", key)
            return
        if preference.getValue() == preference.getDefault():
            self.setValue(key, default_value)
        preference.setDefault(default_value)

    def setValue(self, key: str, value: Any) -> None:
        preference = self._findPreference(key)

        if preference:
            preference.setValue(value)
        else:
            Logger.log("w", "Tried to set the value of non-existing setting %s.", key)

    def getValue(self, key: str) -> Any:
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

    def resetPreference(self, key: str) -> None:
        preference = self._findPreference(key)

        if preference:
            preference.setValue(preference.getDefault())

    def readFromFile(self, file: Union[str, IO[str]]) -> None:
        self._loadFile(file)

        self.__initializeSettings()

    def __initializeSettings(self) -> None:
        if self._parser is None:
            Logger.log("w", "Read the preferences file before initializing settings!")
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

    def writeToFile(self, file: Union[str, IO[str]]) -> None:
        parser = configparser.ConfigParser(interpolation = None) #pylint: disable=bad-whitespace
        for group, group_entries in self._preferences.items():
            parser[group] = {}
            for key, pref in group_entries.items():
                if pref.getValue() != pref.getDefault():
                    parser[group][key] = str(pref.getValue())

        parser["general"]["version"] = str(Preferences.Version)

        try:
            if hasattr(file, "read"):  # If it already is a stream like object, write right away
                parser.write(file) #type: ignore #Can't convince MyPy that it really is an IO object now.
            else:
                with SaveFile(file, "wt") as save_file:
                    parser.write(save_file)
        except Exception as e:
            Logger.log("e", "Failed to write preferences to %s: %s", file, str(e))

    def _splitKey(self, key: str) -> Tuple[str, str]:
        group = "general"
        key = key

        if "/" in key:
            parts = key.split("/")
            group = parts[0]
            key = parts[1]

        return (group, key)

    def _findPreference(self, key: str) -> Optional[Any]:
        group, key = self._splitKey(key)

        if group in self._preferences:
            if key in self._preferences[group]:
                return self._preferences[group][key]

        return None

    def _loadFile(self, file: Union[str, IO[str]]) -> None:
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
            Logger.logException("e", "An exception occurred while trying to read preferences file")
            self._parser = None
            return

        del self._parser["general"]["version"]

    ##  Extract data from string and store it in the Configuration parser.
    def deserialize(self, serialized: str) -> None:
        self._parser = configparser.ConfigParser(interpolation=None)
        self._parser.read_string(serialized)
        has_version = "general" in self._parser and "version" in self._parser["general"]

        if has_version:
            if self._parser["general"]["version"] != str(Preferences.Version):
                Logger.log("w", "Could not deserialize preferences from loaded project")
                self._parser = None
                return
        else:
            return

        self.__initializeSettings()


class _Preference:
    def __init__(self, name: str, default: Any = None, value: Any = None) -> None:  # pylint: disable=bad-whitespace
        self._name = name
        self._default = default
        self._value = default if value is None else value

    def getName(self) -> str:
        return self._name

    def getValue(self) -> Any:
        return self._value

    def getDefault(self) -> Any:
        return self._default

    def setDefault(self, default: Any) -> None:
        self._default = default

    def setValue(self, value: Any) -> None:
        self._value = value
