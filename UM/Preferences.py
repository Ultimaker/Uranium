# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser
from typing import Any, Dict, IO, Optional, Tuple, Union

from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType #To register the MIME type of the preference file.
from UM.SaveFile import SaveFile
from UM.Signal import Signal, signalemitter

MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-preferences",
        comment = "Uranium Preferences File",
        suffixes = ["cfg"],
        preferred_suffix = "cfg"
    )
)


@signalemitter
class Preferences:
    """Preferences are application based settings that are saved for future use.

    Typical preferences would be window size, standard machine, etc.
    The application preferences can be gotten from the getPreferences() function in Application
    """

    Version = 6

    def __init__(self) -> None:
        super().__init__()

        self._parser = None  # type: Optional[configparser.ConfigParser]
        self._preferences = {}  # type: Dict[str, Dict[str, _Preference]]

    def addPreference(self, key: str, default_value: Any) -> None:
        """Add a new preference to the list.

        If the preference was already added, it's default is set to whatever is provided
        """

        if key.count("/") != 1:
            raise Exception("Preferences must be in the [CATEGORY]/[KEY] format")
        preference = self._findPreference(key)
        if preference:
            self.setDefault(key, default_value)
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

    def setDefault(self, key: str, default_value: Any) -> None:
        """Changes the default value of a preference.

        If the preference is currently set to the old default, the value of the
        preference will be set to the new default.

        :param key: The key of the preference to set the default of.
        :param default_value: The new default value of the preference.
        """

        preference = self._findPreference(key)
        if not preference:  # Key not found.
            Logger.log("w", "Tried to set the default value of non-existing setting %s.", key)
            return
        if preference.getValue() == preference.getDefault():
            self.setValue(key, default_value)
        preference.setDefault(default_value)

    def setValue(self, key: str, value: Any) -> None:
        preference = self._findPreference(key)
        if preference:
            if preference.getValue() != value:
                preference.setValue(value)
                self.preferenceChanged.emit(key)
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
            if preference.getValue() != preference.getDefault():
                preference.setValue(preference.getDefault())
                self.preferenceChanged.emit(key)
        else:
            Logger.log("w", "Tried to reset unknown setting %s", key)

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
                self.preferenceChanged.emit("{0}/{1}".format(group, key))

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

    # A lot of things listen in on the preference changed signal, so always queue it for the next frame.
    preferenceChanged = Signal(Signal.Queued)

    def _splitKey(self, key: str) -> Tuple[str, str]:
        group = "general"
        key = key

        if "/" in key:
            parts = key.split("/")
            group = parts[0]
            key = parts[1]

        return group, key

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

    def deserialize(self, serialized: str) -> None:
        """Extract data from string and store it in the Configuration parser."""

        updated_preferences = self.__updateSerialized(serialized)
        self._parser = configparser.ConfigParser(interpolation = None)
        try:
            self._parser.read_string(updated_preferences)
        except (configparser.MissingSectionHeaderError, configparser.DuplicateOptionError, configparser.DuplicateSectionError, configparser.ParsingError, configparser.InterpolationError) as e:
            Logger.log("w", "Could not deserialize preferences file: {error}".format(error = str(e)))
            self._parser = None
            return
        has_version = "general" in self._parser and "version" in self._parser["general"]

        if has_version:
            if self._parser["general"]["version"] != str(Preferences.Version):
                Logger.log("w", "Could not deserialize preferences from loaded project")
                self._parser = None
                return
        else:
            return

        self.__initializeSettings()

    def __updateSerialized(self, serialized: str) -> str:
        """Updates the given serialized data to the latest version."""

        configuration_type = "preferences"

        try:
            from UM.VersionUpgradeManager import VersionUpgradeManager
            version = VersionUpgradeManager.getInstance().getFileVersion(configuration_type, serialized)
            if version is not None:
                result = VersionUpgradeManager.getInstance().updateFilesData(configuration_type, version, [serialized], [""])
                if result is not None:
                    serialized = result.files_data[0]
        except:
            Logger.logException("d", "An exception occurred while trying to update the preferences.")
        return serialized


class _Preference:
    def __init__(self, name: str, default: Any = None, value: Any = None) -> None:
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
