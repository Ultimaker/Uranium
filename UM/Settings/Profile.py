# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser
from copy import deepcopy
import io #For serialising the profile to strings.

from UM.Signal import Signal, SignalEmitter
from UM.Settings import SettingsError
from UM.Logger import Logger
from UM.Settings.Validators.ResultCodes import ResultCodes
from UM.SaveFile import SaveFile

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

##  Provides a collection of setting values
#
#   The profile class handles setting values for "user" settings. User settings are settings
#   that can be adjusted by users, as opposed to machine settings which are mostly intrinsic
#   values of the machine, but which can optionally be overridden from MachineInstance.
#
#   The Profile class provides getters and setters for setting values, in addition to
#   serialization and deserialization methods. There are a couple of intrinsic properties for a
#   profile eg a name, which is used as a human-readable identifier and a read only property.
#   Read only profiles are profiles that should not be modified because they are read from system
#   locations that cannot be written to, for example /usr/share on Linux systems.
#
#   Each machine instance has a single "working profile" which has the current settings for this
#   machine instance. This working profile is different in that it can also stores the settings
#   of the profile(s) it was based on. This is done so settings can be reset to the value of the
#   profile the working profile was based on.
class Profile(SignalEmitter):
    ProfileVersion = 1

    ##  Constructor.
    def __init__(self, machine_manager, read_only = False):
        super().__init__()
        self._machine_manager = machine_manager
        self._changed_settings = {}
        self._changed_settings_defaults = {}
        self._name = catalog.i18nc("@label", "Current settings")
        self._type = None
        self._machine_type_id = None
        self._machine_variant_name = None
        self._machine_instance_name = None
        self._material_name = None
        self._read_only = read_only
        self._dirty = True

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
            self._name = self._machine_manager.makeUniqueProfileName(name, old_name)
            self.nameChanged.emit(self, old_name)

    ##  Set whether this profile should be considered a read only profile.
    def setReadOnly(self, read_only):
        self._read_only = read_only

    ##  Retrieve if this profile is a read only profile.
    def isReadOnly(self):
        return self._read_only

    ##  Set the type of this profile.
    def setType(self, type):
        self._type = type

    ##  Retrieve the type of this profile.
    def getType(self):
        return self._type

    ##  Retrieve the name of the machine type.
    def getMachineTypeId(self):
        return self._machine_type_id

    ##  Set the name of the machine type.
    def setMachineTypeId(self, machine_type):
        self._machine_type_id = machine_type

    ##  Retrieve the name of the machine variant.
    def getMachineVariantName(self):
        return self._machine_variant_name

    ##  Set the name of the machine type.
    def setMachineVariantName(self, machine_variant):
        self._machine_variant_name = machine_variant

    ##  Retrieve the name of the machine instance.
    def getMachineInstanceName(self):
        return self._machine_instance_name

    ##  Set the name of the machine type.
    def setMachineInstanceName(self, machine_instance):
        self._machine_instance_name = machine_instance

    ##  Retrieve the name of the material.
    def getMaterialName(self):
        return self._material_name

    ##  Set the name of the machine type.
    def setMaterialName(self, material):
        self._material_name = material

    ##  Get whether the profile has unsaved changed
    def hasUnsavedChanges(self):
        return self._dirty

    ##  Emitted whenever a setting value changes.
    #
    #   \param key \type{string} The key of the setting that changed.
    settingValueChanged = Signal()

    ##  Set a certain setting value.
    #
    #   \param key The key of the setting to set.
    #   \param value The new value of the setting.
    #   \param silent Make the call less verbose, used when loading profiles
    #
    #   \note If the setting is not a user-settable setting, this method will do nothing.
    def setSettingValue(self, key, value, silent = False):
        if not silent:
            Logger.log("d", "Setting value of %s to %s on profile %s", key, value, self._name)

        self._dirty = True

        if not self._active_instance:
            #Active profile is not yet set, so we can't check against machine definition or default values.
            #This happens when loading profiles on first start of Cura.
            self._changed_settings[key] = value
            return

        if not self._active_instance.getMachineDefinition().isUserSetting(key):
            Logger.log("w", "Tried to set value of non-user setting %s", key)
            return

        setting = self._active_instance.getMachineDefinition().getSetting(key)
        if not setting:
            return

        if value == setting.getDefaultValue() or value == str(setting.getDefaultValue()) and not self._type:
            #Note: partial profiles can have values that equal the default setting
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
            self._onActiveInstanceChanged()

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

    ##  Reset the settings that have a value set in this profile to a new set.
    def setChangedSettings(self, settings):
        self._changed_settings = settings
        self._dirty = True

    ##  Get a dictionary of all setting values.
    #
    #   \param kwargs Keyword arguments.
    #                 Possible values:
    #                 - include_machine \type{bool} Include machine settings.
    def getAllSettingValues(self, **kwargs):
        values = { }

        if not self._active_instance:
            self._onActiveInstanceChanged()

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
                continue

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
            setting = self._active_instance.getMachineDefinition().getSetting(key)
            if not setting:
                return False
            valid = setting.validate(value)
            if valid == ResultCodes.min_value_error or valid == ResultCodes.max_value_error or valid == ResultCodes.not_valid_error:
                Logger.log("w", "The setting %s has an invalid value of %s", key, value)
                return True

        return False

    ##  Check whether this profile has a value for a certain setting.
    #   /param key The key for the setting to check
    #   /param filter_defaults Don't include setting if its value equals the default setting for this profile
    def hasSettingValue(self, key, filter_defaults = False):
        if filter_defaults:
            return key in self._changed_settings and ( key not in self._changed_settings_defaults or self._changed_settings[key] != self._changed_settings_defaults[key])
        else:
            return key in self._changed_settings

    ## Check whether this profile has any changed settings that are different from the default.
    def hasChangedSettings(self):
        for key in self._changed_settings:
            if self.hasSettingValue(key, filter_defaults = True):
                return True

    ##  Remove a setting value from this profile, resetting it to its default value.
    def resetSettingValue(self, key):
        if key not in self._changed_settings:
            return

        if key in self._changed_settings_defaults:
            self._changed_settings[key] = self._changed_settings_defaults[key]
        else:
            del self._changed_settings[key]

        self.settingValueChanged.emit(key)

    ## Merge settings from another profile
    def mergeSettingsFrom(self, profile, reset = False):
        if reset:
            self._changed_settings = {}
            self._changed_settings_defaults = {}

        if not profile:
            return

        settings = profile.getChangedSettings()

        for key, value in settings.items():
            self._changed_settings[key] = value
            self._changed_settings_defaults[key] = value

        self._dirty = True

    ##  Load a serialised profile from a file.
    #
    #   The read is currently not atomic, only the write is. So this method
    #   assumes that there are no other processes than this Cura instance
    #   writing to the file. If there are, the ConfigParser will likely fail
    #   (but the file doesn't get corrupt).
    #   \param path The path to the file to load from.
    def loadFromFile(self, path):
        f = open(path) #Open file for reading.
        serialised = f.read()
        self.unserialise(serialised, path) #Unserialise the serialised contents that we found in that file.
        self._dirty = False

    ##  Load a serialized profile from a string.
    #
    #   The unserialised profile is saved in this instance.
    #   \param serialised A string containing the serialised form of the
    #   profile.
    #   \param origin A string representing the origin of this serialised
    #   string. This is only used when an error occurs.
    def unserialise(self, serialised, origin = "(unknown)"):
        stream = io.StringIO(serialised) #ConfigParser needs to read from a stream.
        parser = configparser.ConfigParser(interpolation = None)
        parser.readfp(stream)

        if not parser.has_section("general"):
            raise SettingsError.InvalidFileError(origin)

        if not parser.has_option("general", "version") or int(parser.get("general", "version")) != self.ProfileVersion:
            raise SettingsError.InvalidVersionError(origin)

        self._name = parser.get("general", "name")
        if "type" in parser["general"]:
            self._type = parser.get("general", "type")
        if "machine_type" in parser["general"]:
            self._machine_type_id = parser.get("general", "machine_type")
        if "machine_variant" in parser["general"]:
            self._machine_variant_name = parser.get("general", "machine_variant")
        if "machine_instance" in parser["general"]:
            self._machine_instance_name = parser.get("general", "machine_instance")
        if "material" in parser["general"]:
            self._material_name = parser.get("general", "material")
        elif self._type == "material" and "name" in parser["general"]:
            self._material_name = parser.get("general", "name")

        if parser.has_section("settings"):
            for key, value in parser["settings"].items():
                self.setSettingValue(key, value, silent = True)

        if parser.has_section("defaults"):
            self._changed_settings_defaults = {}
            for key, value in parser["defaults"].items():
                self._changed_settings_defaults[key] = value

    ##  Store this profile in a file so it can be loaded later.
    #
    #   \param file The file to save the profile to.
    def saveToFile(self, file):
        serialised = self.serialise() #Serialise this profile instance to a string.
        try:
            with SaveFile(file, "wt", -1, "utf-8") as f: #Open the specified file.
                f.write(serialised)
        except Exception as e:
            Logger.log("e", "Failed to write profile to %s: %s", file, str(e))
            return str(e)

        self._dirty = False
        return None

    ##  Serialise this profile to a string.
    def serialise(self):
        stream = io.StringIO() #ConfigParser needs to write to a stream.
        parser = configparser.ConfigParser(interpolation = None)

        parser.add_section("general") #Write a general section.
        parser.set("general", "version", str(self.ProfileVersion))
        parser.set("general", "name", self._name)
        if self._type:
            parser.set("general", "type", self._type)
        if self._machine_type_id:
            parser.set("general", "machine_type", self._machine_type_id)
        if self._machine_variant_name:
            parser.set("general", "machine_variant", self._machine_variant_name)
        if self._machine_instance_name:
            parser.set("general", "machine_instance", self._machine_instance_name)
        if self._material_name and not self._type:
            parser.set("general", "material", self._material_name)

        parser.add_section("settings") #Write each changed setting in a settings section.
        for setting_key in self._changed_settings:
            parser.set("settings", setting_key , str(self._changed_settings[setting_key]))

        if len(self._changed_settings_defaults) > 0:
            parser.add_section("defaults") #Write each changed setting in a settings section.
            for setting_key in self._changed_settings_defaults:
                parser.set("defaults", setting_key , str(self._changed_settings_defaults[setting_key]))

        parser.write(stream) #Actually serialise it to the stream.
        return stream.getvalue()

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
        if setting.getKey() not in self._changed_settings:
            self.settingValueChanged.emit(setting.getKey())
