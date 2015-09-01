# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import urllib
import os
import json

from UM.Signal import Signal, SignalEmitter
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Preferences import Preferences

from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineInstance import MachineInstance
from UM.Settings.Profile import Profile
from UM.Settings.SettingsError import SettingsError

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

        Preferences.getInstance().addPreference("machines/setting_visibility", "")
        Preferences.getInstance().addPreference("machines/active_instance", "")
        Preferences.getInstance().addPreference("machines/active_profile", "")

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

    machineInstancesChanged = Signal()

    machineInstanceNameChanged = Signal()

    def getMachineInstance(self, index):
        return self._machine_instances[index]

    def getMachineInstances(self):
        return self._machine_instances

    def addMachineInstance(self, instance):
        if instance in self._machine_instances:
            return

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
            self.setActiveMachineInstance(self._machine_instances[0])

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
            setting_visibility = self._active_machine.getAllSettings(visible_only = True)
            setting_visibility = list(map(lambda s: s.getKey(), setting_visibility))

        self._active_machine = machine

        self._updateSettingVisibility(setting_visibility)

        Preferences.getInstance().setValue("machines/active_instance", self._active_machine.getName())

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
            self.setActiveProfile(self._profiles[0])

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

        Preferences.getInstance().setValue("machines/active_profile", self._active_profile.getName())

        self.activeProfileChanged.emit()

    def loadAll(self):
        self.loadMachineDefinitions()
        self.loadMachineInstances()
        self.loadProfiles()
        self.loadVisibility()

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
        for instance in self._machine_instances:
            file_name = urllib.parse.quote_plus(instance.getName()) + ".cfg"
            instance.saveToFile(Resources.getStoragePath(Resources.MachineInstances, file_name))

    def saveProfiles(self):
        for profile in self._profiles:
            if profile.isReadOnly():
                continue

            file_name = urllib.parse.quote_plus(profile.getName()) + ".cfg"
            profile.saveToFile(Resources.getStoragePath(Resources.Profiles, file_name))

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
