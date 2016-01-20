# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import urllib
import os
import json

from UM.Signal import Signal, SignalEmitter
from UM.Resources import Resources
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry #For registering profile reader plugins.
from UM.Preferences import Preferences

from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.Profile import Profile
from UM.Settings import SettingsError

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class MachineManager(SignalEmitter):
    def __init__(self, app_name):
        super().__init__()

        self._application_name = app_name

        self._machine_definitions = []
        self._machine_instances = []
        self._profiles = []

        self._active_machine = None
        self._active_profile = None

        self._profile_readers = {} #Plugins that read profiles from file.
        self._profile_writers = {} #Plugins that write profiles to file.
        PluginRegistry.addType("profile_reader", self.addProfileReader)
        PluginRegistry.addType("profile_writer", self.addProfileWriter)

        Preferences.getInstance().addPreference("machines/setting_visibility", "")
        Preferences.getInstance().addPreference("machines/active_instance", "")
        Preferences.getInstance().addPreference("machines/active_profile", "Normal Quality")

    def getApplicationName(self):
        return self._application_name

    machineDefinitionsChanged = Signal()

    def getMachineDefinitions(self, **kwargs):
        if kwargs.get("include_variants", True):
            return self._machine_definitions

        definitions = []
        variant_ids = []
        for definition in self._machine_definitions:
            if not definition.getVariantName() or definition.getId() not in variant_ids:
                definitions.append(definition)
                variant_ids.append(definition.getId())

        return definitions

    def getAllMachineVariants(self, machine_id):
        variants = []
        for definition in self._machine_definitions:
            if definition.getId() == machine_id:
                variants.append(definition)

        return variants

    def findMachineDefinition(self, machine_id, variant_name = None):
        for definition in self._machine_definitions:
            if definition.getId() == machine_id:
                if variant_name:
                    if definition.getVariantName() == variant_name:
                        return definition
                else:
                    return definition

        return None

    addMachineRequested = Signal()

    machineInstancesChanged = Signal()

    machineInstanceNameChanged = Signal()

    def getMachineInstance(self, index):
        return self._machine_instances[index]

    def getMachineInstances(self):
        return self._machine_instances

    def addMachineInstance(self, instance):
        if instance in self._machine_instances:
            return

        for i in self._machine_instances:
            if i.getName() == instance.getName():
                raise SettingsError.DuplicateMachineInstanceError(instance.getName())

        self._machine_instances.append(instance)
        instance.nameChanged.connect(self._onInstanceNameChanged)
        self.machineInstancesChanged.emit()

    def removeMachineInstance(self, instance):
        if instance not in self._machine_instances:
            return

        self._machine_instances.remove(instance)
        instance.nameChanged.disconnect(self._onInstanceNameChanged)

        try:
            path = Resources.getStoragePath(Resources.MachineInstances, urllib.parse.quote_plus(instance.getName()) + ".cfg")
            os.remove(path)
        except FileNotFoundError:
            pass

        self.machineInstancesChanged.emit()

        if self._active_machine == instance:
            try:
                self.setActiveMachineInstance(self._machine_instances[0])
            except:
                self.setActiveMachineInstance(None)

    def findMachineInstance(self, name):
        for instance in self._machine_instances:
            if instance.getName() == name:
                return instance

        return None

    ##  Get the currently active machine instance
    #   \returns active_machine \type{MachineSettings}
    def getActiveMachineInstance(self):
        return self._active_machine

    ##  Set the currently active machine
    #   \param active_machine \type{MachineSettings}
    def setActiveMachineInstance(self, machine):
        if machine == self._active_machine:
            return
        setting_visibility = []
        if self._active_machine:
            setting_visibility = self._active_machine.getMachineDefinition().getAllSettings(visible_only = True)
            setting_visibility = list(map(lambda s: s.getKey(), setting_visibility))

        self._active_machine = machine

        self._updateSettingVisibility(setting_visibility)

        self.activeMachineInstanceChanged.emit()

    def setActiveMachineVariant(self, variant):
        if not self._active_machine:
            return

        variant = self.findMachineDefinition(self._active_machine.getMachineDefinition().getId(), variant)
        if not variant:
            return

        setting_visibility = []
        if self._active_machine:
            setting_visibility = self._active_machine.getMachineDefinition().getAllSettings(visible_only = True)
            setting_visibility = list(map(lambda s: s.getKey(), setting_visibility))

        self._active_machine.setMachineDefinition(variant)

        self._updateSettingVisibility(setting_visibility)

        self.activeMachineInstanceChanged.emit()

    activeMachineInstanceChanged = Signal()

    profilesChanged = Signal()

    profileNameChanged = Signal()

    def getProfiles(self):
        return self._profiles

    def addProfile(self, profile):
        if profile in self._profiles:
            return

        for p in self._profiles:
            if p.getName() == profile.getName():
                raise SettingsError.DuplicateProfileError(profile.getName())

        self._profiles.append(profile)
        profile.nameChanged.connect(self._onProfileNameChanged)
        self.profilesChanged.emit()

    def removeProfile(self, profile):
        if profile not in self._profiles:
            return

        self._profiles.remove(profile)
        profile.nameChanged.disconnect(self._onProfileNameChanged)

        try:
            path = Resources.getStoragePath(Resources.Profiles, urllib.parse.quote_plus(profile.getName()) + ".cfg")
            os.remove(path)
        except FileNotFoundError:
            pass

        self.profilesChanged.emit()

        if profile == self._active_profile:
            try:
                self.setActiveProfile(self._profiles[0])
            except:
                self.setActiveProfile(None)

    def findProfile(self, name):
        for profile in self._profiles:
            if profile.getName() == name:
                return profile

        return None

    activeProfileChanged = Signal()

    def getActiveProfile(self):
        return self._active_profile

    def setActiveProfile(self, profile):
        if profile not in self._profiles or self._active_profile == profile:
            return

        self._active_profile = profile

        # This is called at this point, as this is the first point that we know
        # there is a profile, which the update requires to run.
        self._active_machine.getMachineDefinition().updateRequiredBySettings()

        self.activeProfileChanged.emit()

    def loadAll(self):
        self.loadMachineDefinitions()
        self.loadMachineInstances()
        self.loadProfiles()
        self.loadVisibility()

    def addMachineDefinition(self, definition):
        if not self.findMachineDefinition(definition.getId(), definition.getVariantName()):
            self._machine_definitions.append(definition)
            self.machineDefinitionsChanged.emit()

    def loadMachineDefinitions(self):
        dirs = Resources.getAllPathsForType(Resources.MachineDefinitions)
        for dir in dirs:
            if not os.path.isdir(dir):
                continue

            for file_name in os.listdir(dir):
                data = None
                path = os.path.join(dir, file_name)

                if os.path.isdir(path):
                    continue

                definition = MachineDefinition(self, path)
                try:
                    definition.loadMetaData()
                except Exception as e:
                    Logger.log("e", "An error occurred loading Machine Definition %s: %s", path, str(e))
                    continue

                # Only add the definition if it did not exist yet. This prevents duplicates.
                # We don't use addMachineDefinition to prevent signal spam.
                if not self.findMachineDefinition(definition.getId(), definition.getVariantName()):
                    self._machine_definitions.append(definition)
        self.machineDefinitionsChanged.emit()

    def loadMachineInstances(self):
        dirs = Resources.getAllPathsForType(Resources.MachineInstances)
        for dir in dirs:
            if not os.path.isdir(dir):
                continue

            for file_name in os.listdir(dir):
                path = os.path.join(dir, file_name)

                if os.path.isdir(path):
                    continue

                instance = MachineInstance(self)
                try:
                    instance.loadFromFile(path)
                except Exception as e:
                    Logger.log("e", "An exception occurred loading Machine Instance: %s: %s", path, str(e))
                    continue

                if not self.findMachineInstance(instance.getName()):
                    self._machine_instances.append(instance)
                    instance.nameChanged.connect(self._onInstanceNameChanged)

        instance = self.findMachineInstance(Preferences.getInstance().getValue("machines/active_instance"))
        if instance:
            self.setActiveMachineInstance(instance)

        self.machineInstancesChanged.emit()

    def loadProfiles(self):
        storage_path = Resources.getStoragePathForType(Resources.Profiles)

        dirs = Resources.getAllPathsForType(Resources.Profiles)
        for dir in dirs:
            if not os.path.isdir(dir):
                continue

            read_only = dir != storage_path

            for file_name in os.listdir(dir):
                path = os.path.join(dir, file_name)

                if os.path.isdir(path):
                    continue

                profile = Profile(self, read_only)
                try:
                    profile.loadFromFile(path)
                except Exception as e:
                    Logger.log("e", "An exception occurred loading Profile %s: %s", path, str(e))
                    continue

                if not self.findProfile(profile.getName()):
                    self._profiles.append(profile)
                    profile.nameChanged.connect(self._onProfileNameChanged)

        profile = self.findProfile(Preferences.getInstance().getValue("machines/active_profile"))
        if profile:
            self.setActiveProfile(profile)
        else:
            if Preferences.getInstance().getValue("machines/active_profile") == "":
                for profile in self._profiles:
                    self.setActiveProfile(profile) #default to first profile you can find
                    break
        self.profilesChanged.emit()

    def loadVisibility(self):
        preference = Preferences.getInstance().getValue("machines/setting_visibility")
        if not preference or not self._active_machine:
            return

        self._updateSettingVisibility(preference.split(","))

    def saveAll(self):
        self.saveMachineInstances()
        self.saveProfiles()
        self.saveVisibility()

    def saveMachineInstances(self):
        if self._active_machine:
            Preferences.getInstance().setValue("machines/active_instance", self._active_machine.getName())

        for instance in self._machine_instances:
            file_name = urllib.parse.quote_plus(instance.getName()) + ".cfg"
            instance.saveToFile(Resources.getStoragePath(Resources.MachineInstances, file_name))

    def saveProfiles(self):
        try:
            Preferences.getInstance().setValue("machines/active_profile", self._active_profile.getName())
            for profile in self._profiles:
                if profile.isReadOnly():
                    continue

                file_name = urllib.parse.quote_plus(profile.getName()) + ".cfg"
                profile.saveToFile(Resources.getStoragePath(Resources.Profiles, file_name))
        except AttributeError:
            pass

    ##  Adds a new profile reader plugin.
    #
    #   \param reader The plugin to read profiles with.
    def addProfileReader(self, reader):
        self._profile_readers[reader.getPluginId()] = reader

    ##  Adds a new profile writer plugin.
    #
    #   \param writer The plugin to write profiles with.
    def addProfileWriter(self, writer):
        self._profile_writers[writer.getPluginId()] = writer

    ##  Returns an iterable of all profile readers.
    #
    #   \return All profile readers that are currently loaded.
    def getProfileReaders(self):
        return self._profile_readers.items()

    ##  Returns an iterable of all profile writers.
    #
    #   \return All profile writers that are currently loaded.
    def getProfileWriters(self):
        return self._profile_writers.items()

    ##  Returns a dictionary of the file types the profile readers can read.
    #
    #   Each file extension should have a description.
    #
    #   \return A dictionary of the file types the profile readers can read.
    def getSupportedProfileTypesRead(self):
        supported_types = {}
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"profile_reader": {}}, active_only = True)
        for plugin in meta_data:
            if "profile_reader" in plugin:
                for supported_type in plugin["profile_reader"]: #All extensions that this plugin can supposedly read.
                    extension = supported_type.get("extension", None)
                    if extension:
                        description = supported_type.get("description", extension)
                        supported_types[extension] = description

        return supported_types

    ##  Returns a dictionary of the file types the profile writers can write.
    #
    #   Each file extension should have a description.
    #
    #   \return A dictionary of the file types the profile writers can write.
    def getSupportedProfileTypesWrite(self):
        supported_types = {}
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter = {"profile_writer": {}}, active_only = True)
        for plugin in meta_data:
            if "profile_writer" in plugin:
                for supported_type in plugin["profile_writer"]: #All extensions that this plugin can supposedly write.
                    extension = supported_type.get("extension", None)
                    if extension:
                        description = supported_type.get("description", extension)
                        supported_types[extension] = description

        return supported_types

    def saveVisibility(self):
        if not self._active_machine:
            Logger.log("w", "No active machine found when trying to save setting visibility")
            return

        visible_settings = self._active_machine.getMachineDefinition().getAllSettings(visible_only = True)
        visible_settings = map(lambda s: s.getKey(), visible_settings)

        preference = ",".join(visible_settings)
        Preferences.getInstance().setValue("machines/setting_visibility", preference)

    def _updateSettingVisibility(self, visible_keys):
        if not visible_keys:
            return

        for setting in self._active_machine.getMachineDefinition().getAllSettings():
            if setting.getKey() in visible_keys:
                setting.setVisible(True)
            else:
                setting.setVisible(False)

    def _onInstanceNameChanged(self, instance, old_name):
        file_name = urllib.parse.quote_plus(old_name) + ".cfg"
        try:
            path = Resources.getStoragePath(Resources.MachineInstances, file_name)
            os.remove(path)
        except FileNotFoundError:
            pass

        self.machineInstanceNameChanged.emit(instance)

    def _onProfileNameChanged(self, profile, old_name):
        file_name = urllib.parse.quote_plus(old_name) + ".cfg"
        try:
            path = Resources.getStoragePath(Resources.Profiles, file_name)
            os.remove(path)
        except FileNotFoundError:
            pass

        self.profileNameChanged.emit(profile)
