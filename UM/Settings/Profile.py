# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser
from copy import deepcopy

from UM.Signal import Signal, SignalEmitter
from UM.Settings import SettingsError
from UM.Logger import Logger
from UM.Settings.Validators.ResultCodes import ResultCodes
from UM.SaveFile import SaveFile

##  Provides a collection of setting values
#
#   The profile class handles setting values for "user" settings. User settings are settings
#   that can be adjusted by users, as opposed to machine settings which are mostly intrinsic
#   values of the machine, but which can optionally be overridden from MachineInstance.
#
#   The Profile class provides getters and setters for setting values, in addition to
#   serialization and deserialization methods. There are two intrinsic properties for a profile,
#   its name, which is used as a human-readable identifier and a read only property. Read only
#   profiles are profiles that should not be modified because they are read from system locations
#   that cannot be written to, for example /usr/share on Linux systems.
class Profile(SignalEmitter):
    ProfileVersion = 1

    ##  Constructor.
    def __init__(self, machine_manager, read_only = False):
        super().__init__()
        self._machine_manager = machine_manager
        self._changed_settings = {}
        self._name = "Unknown Profile"
        self._read_only = read_only

        self._active_instance = None
        self._machine_manager.activeMachineInstanceChanged.connect(self._onActiveInstanceChanged)
        self._onActiveInstanceChanged()

    ##  Emitted when the name of the profile changes.
    nameChanged = Signal()

    ##  Retrieve the name of the profile.
    def getName(self):
        return self._name

    ##  Set the name of the profile.
    #
    #   \param name \type{string} The new name of the profile.
    def setName(self, name):
        if name != self._name:
            old_name = self._name
            self._name = name
            self.nameChanged.emit(self, old_name)

    ##  Set whether this profile should be considered a read only profile.
    def setReadOnly(self, read_only):
        self._read_only = read_only

    ##  Retrieve if this profile is a read only profile.
    def isReadOnly(self):
        return self._read_only

    ##  Emitted whenever a setting value changes.
    #
    #   \param key \type{string} The key of the setting that changed.
    settingValueChanged = Signal()

    ##  Set a certain setting value.
    #
    #   \param key The key of the setting to set.
    #   \param value The new value of the setting.
    #
    #   \note If the setting is not a user-settable setting, this method will do nothing.
    def setSettingValue(self, key, value):
        Logger.log('d' , "Setting value of setting %s to %s",key,value)

        if not self._active_instance or not self._active_instance.getMachineDefinition().isUserSetting(key):
            Logger.log("w", "Tried to set value of non-user setting %s", key)
            return

        setting = self._active_instance.getMachineDefinition().getSetting(key)
        if not setting:
            return

        if value == setting.getDefaultValue() or value == str(setting.getDefaultValue()):
            if key in self._changed_settings:
                del self._changed_settings[key]
                self.settingValueChanged.emit(key)

            return

        if key in self._changed_settings and self._changed_settings[key] == value:
            return

        self._changed_settings[key] = value
        self.settingValueChanged.emit(key)

    ##  Get the value of a setting.
    #
    #   This method will retrieve the value of a setting. If the value has been set in the profile, it will
    #   return the value from the profile. If the value was not set, it will fall back to the active machine
    #   instance and call MachineInstance::getSettingValue().
    #
    #   \param key \type{string} The key of the setting to retrieve the value for.
    def getSettingValue(self, key):
        if not self._active_instance:
            return None

        setting = self._active_instance.getMachineDefinition().getSetting(key)
        if not setting:
            return None

        if key in self._changed_settings:
            return setting.parseValue(self._changed_settings[key])

        return self._active_instance.getSettingValue(key)

    ##  Get a dictionary of all settings that have a value set in this profile.
    def getChangedSettings(self):
        return self._changed_settings

    ##  Get a dictionary of all setting values.
    #
    #   \param kwargs Keyword arguments.
    #                 Possible values:
    #                 - include_machine \type{bool} Include machine settings.
    def getAllSettingValues(self, **kwargs):
        values = { }

        if not self._active_instance:
            return values

        settings = self._active_instance.getMachineDefinition().getAllSettings(include_machine = kwargs.get("include_machine", False))

        for setting in settings:
            key = setting.getKey()

            if key in self._changed_settings:
                values[key] = setting.parseValue(self._changed_settings[key])
                continue

            if self._active_instance.hasMachineSettingValue(key):
                values[key] = self._active_instance.getMachineSettingValue(key)

            values[key] = setting.getDefaultValue(self)

        return values

    ##  Get a dictionary of all settings with changed values and their children.
    #
    #   Since children can have inheritance functions we need to recalculate the setting
    #   values based on the setting values from this profile.
    def getChangedSettingValues(self):
        values = {}

        if not self._active_instance:
            return values

        definition = self._active_instance.getMachineDefinition()

        for key, value in self._changed_settings.items():
            setting = definition.getSetting(key)
            if not setting:
                continue

            values[key] = setting.parseValue(value)

            for child in setting.getAllChildren():
                child_key = child.getKey()
                if child_key in self._changed_settings:
                    values[child_key] = child.parseValue(self._changed_settings[child_key])
                else:
                    values[child_key] = child.getDefaultValue(self)

        return values

    ##  Validate all settings and check if any setting has an error.
    def hasErrorValue(self):
        for key, value in self._changed_settings.items():
            valid = self._active_instance.getMachineDefinition().getSetting(key).validate(value)
            if valid == ResultCodes.min_value_error or valid == ResultCodes.max_value_error or valid == ResultCodes.not_valid_error:
                Logger.log("w", "The setting %s has an invalid value of %s",key,value)
                return True

        return False

    ##  Check whether this profile has a value for a certain setting.
    def hasSettingValue(self, key):
        return key in self._changed_settings

    ##  Remove a setting value from this profile, resetting it to its default value.
    def resetSettingValue(self, key):
        if key not in self._changed_settings:
            return

        del self._changed_settings[key]
        self.settingValueChanged.emit(key)

    ##  Load a serialized profile from a file.
    def loadFromFile(self, path):
        parser = configparser.ConfigParser(interpolation = None)
        parser.read(path, "utf-8")

        if not parser.has_section("general"):
            raise SettingsError.InvalidFileError(path)

        if not parser.has_option("general", "version") or int(parser.get("general", "version")) != self.ProfileVersion:
            raise SettingsError.InvalidVersionError(path)

        self._name = parser.get("general", "name")

        if parser.has_section("settings"):
            for key, value in parser["settings"].items():
                self.setSettingValue(key, value)

    ##  Serialize this profile to a file so it can be loaded later.
    def saveToFile(self, file):
        parser = configparser.ConfigParser(interpolation = None)

        parser.add_section("general")
        parser.set("general", "version", str(self.ProfileVersion))
        parser.set("general", "name", self._name)

        parser.add_section("settings")
        for setting_key in self._changed_settings:
            parser.set("settings", setting_key , str(self._changed_settings[setting_key]))
        
        try:
            with SaveFile(file, "wt", -1, "utf-8") as f:
                parser.write(f)
        except Exception as e:
            Logger.log("e", "Failed to write profile to %s: %s", file, str(e))
            return str(e)

        return None

    ##  Reimplemented deepcopy that makes sure we do not copy the machine instance.
    def __deepcopy__(self, memo):
        copy = Profile(self._machine_manager, self._read_only)

        copy._changed_settings = deepcopy(self._changed_settings, memo)
        copy.setName(self._name)

        return copy

    # private:

    def _onActiveInstanceChanged(self):
        if self._active_instance:
            for category in self._active_instance.getMachineDefinition().getAllCategories():
                category.defaultValueChanged.disconnect(self._onDefaultValueChanged)

        self._active_instance = self._machine_manager.getActiveMachineInstance()

        if self._active_instance:
            for category in self._active_instance.getMachineDefinition().getAllCategories():
                category.defaultValueChanged.connect(self._onDefaultValueChanged)

    def _onDefaultValueChanged(self, setting):
        self.settingValueChanged.emit(setting.getKey())
