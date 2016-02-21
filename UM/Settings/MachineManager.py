# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import urllib
import os
import json
import copy
import re

from PyQt5.QtWidgets import QMessageBox #Used in _confirmReplaceCurrentSettings() by lack of a Uranium MessageBox API

import UM #For using UM.Message, which we cannot import here because that would lead to a circular import
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

        self._protect_working_profile = False

        self._profile_readers = {} #Plugins that read profiles from file.
        self._profile_writers = {} #Plugins that write profiles to file.
        PluginRegistry.addType("profile_reader", self.addProfileReader)
        PluginRegistry.addType("profile_writer", self.addProfileWriter)

        Preferences.getInstance().addPreference("machines/setting_visibility", "")
        Preferences.getInstance().addPreference("machines/active_instance", "")

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

    def getAllMachineMaterials(self, instance_id):
        generic_materials = []
        machine_materials = []

        machine = self.findMachineInstance(instance_id)
        if not machine:
            return machine_materials

        machine_type = machine.getMachineDefinition().getProfilesMachineId()
        machine_variant = machine.getMachineDefinition().getVariantName()

        for profile in self._profiles:
            profile_type = profile.getType()
            #Filter out "partial" profiles
            if profile_type == "material":
                generic_materials.append(profile.getName())
                continue

            material = profile.getMaterialName()
            if not material or material in machine_materials:
                continue

            profile_machine_type = profile.getMachineTypeId()
            profile_machine_variant = profile.getMachineVariantName()
            profile_machine_instance = profile.getMachineInstanceName()

            if profile_machine_instance and profile_machine_instance == instance_id:
                machine_materials.append(material)
            elif profile_machine_variant == machine_variant and profile_machine_type == machine_type:
                machine_materials.append(material)

        if len(machine_materials) > 0:
            #This includes Ultigcode printers that have machine-specific material profiles (eg Ultimaker 2+)
            return machine_materials
        else:
            try:
                if machine.getMachineDefinition().getSetting("machine_gcode_flavor").getDefaultValue() == "UltiGCode":
                    #UltiGCode printers don't use the generic set of generic materials (eg Ultimaker 2)
                    return []
            except:
                return []
            return generic_materials


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

        self._setDefaultVariantMaterialProfile(instance)

        self.machineInstancesChanged.emit()

    def removeMachineInstance(self, instance):
        if instance not in self._machine_instances:
            return

        self._machine_instances.remove(instance)
        instance.nameChanged.disconnect(self._onInstanceNameChanged)

        file_name = urllib.parse.quote_plus(instance.getName())
        try:
            path = Resources.getStoragePath(Resources.MachineInstances, file_name + ".cfg")
            os.remove(path)
            path = Resources.getStoragePath(Resources.MachineInstanceProfiles, file_name + ".cfg")
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
            if instance.getName().lower() == name.lower():
                return instance

        return None

    def makeUniqueMachineInstanceName(self, base_name, machine_type_name, old_name = None):
        base_name = base_name.strip()
        num_check = re.compile("(.*?)\s*#\d$").match(base_name)
        if(num_check):
            base_name = num_check.group(1)
        if base_name == "":
            base_name = machine_type_name
        instance_name = base_name
        i = 1
        #Make sure there is no machine instance with the same name,
        #except if it is the old name of the same instance we are renaming
        while self.findMachineInstance(instance_name):
            if instance_name == old_name:
                break
            i = i + 1
            instance_name = "%s #%d" % (base_name, i)

        return instance_name

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

        self._protect_working_profile = True
        profile = self.findProfile(machine.getActiveProfileName(), instance = self._active_machine)
        if profile:
            self.setActiveProfile(profile)
        else:
            for profile in self._profiles:
                self.setActiveProfile(profile) #default to first profile you can find
                break

        if self._active_machine.hasMaterials():
            material = self._active_machine.getMaterialName()
            available_materials = self.getAllMachineMaterials(self._active_machine.getName())
            if not material or (len(available_materials) > 0 and material not in available_materials):
                if "PLA" in available_materials:
                    self._active_machine.setMaterialName("PLA")
                else:
                    self._active_machine.setMaterialName(available_materials[0])

        self.activeMachineInstanceChanged.emit()
        self._protect_working_profile = False

    def setActiveMaterial(self, material):
        if not self._active_machine:
            return

        material_profile = self.findProfile(material, type_name = "material", instance = self._active_machine)
        #This finds only profiles of type "material", which are partial profiles
        if material_profile:
            self._active_machine.getWorkingProfile().mergeSettingsFrom(material_profile, reset = False)
        else:
            #If there are unsaved current settings, confirm with the user before switching variants,
            #because switching variants will load a new profile
            working_profile = self._active_machine.getWorkingProfile()
            if working_profile.hasChangedSettings() and not self._confirmReplaceCurrentSettings(material):
                return

        if material != self._active_machine.getMaterialName():
            self._active_machine.setMaterialName(material)

            #Update the UI if the material selection and/or settings have changed
            self.activeMachineInstanceChanged.emit()

    def setActiveMachineVariant(self, variant):
        if not self._active_machine:
            return

        variant = self.findMachineDefinition(self._active_machine.getMachineDefinition().getId(), variant)
        if not variant:
            return

        #If there are unsaved current settings, confirm with the user before switching variants,
        #because switching variants will load a new profile
        working_profile = self._active_machine.getWorkingProfile()
        if working_profile.hasChangedSettings() and not self._confirmReplaceCurrentSettings(variant.getVariantName()):
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

    def getProfiles(self, type_name = None, instance = None):
        if not instance:
            return self._profiles

        active_machine_type = instance.getMachineDefinition().getProfilesMachineId()
        active_machine_variant = instance.getMachineDefinition().getVariantName()
        active_machine_instance = instance.getName()
        active_machine_material = instance.getMaterialName()

        generic_profiles = []
        specific_profiles = []
        add_generic_profiles = (type_name == None);

        for profile in self._profiles:
            profile_type = profile.getType()
            #Filter out "partial" profiles
            if type_name != "all" and type_name != profile_type:
                continue

            machine_type = profile.getMachineTypeId()
            machine_variant = profile.getMachineVariantName()
            machine_instance = profile.getMachineInstanceName()
            material = profile.getMaterialName()

            if machine_type and machine_type == active_machine_type or machine_type == "all":
                is_specific_profile = False
                if (not machine_instance) and (not machine_variant):
                    is_specific_profile = True
                elif not material or material == active_machine_material:
                    if machine_instance and (machine_instance == active_machine_instance):
                        is_specific_profile = True
                    elif machine_variant and (machine_variant == active_machine_variant):
                        is_specific_profile = True

                if is_specific_profile:
                    specific_profiles.append(profile)
                    if profile.isReadOnly():
                        #There is at least one machine-specific starter-profile, so we don't need the generic profiles
                        add_generic_profiles = False

            elif not machine_type:
                generic_profiles.append(profile)

        if len(specific_profiles) == 0 and type_name == None:
            #No starter-profiles were found
            return generic_profiles

        if add_generic_profiles:
            specific_profiles.extend(generic_profiles)

        return specific_profiles

    def addProfile(self, profile):
        if profile in self._profiles:
            return

        profiles = self.getProfiles(instance = self._active_machine)
        for p in profiles:
            if p.getName() == profile.getName():
                raise SettingsError.DuplicateProfileError(profile.getName())

        self._profiles.append(profile)
        profile.nameChanged.connect(self._onProfileNameChanged)
        self.profilesChanged.emit()

    def addProfileFromWorkingProfile(self):
        profile = copy.deepcopy(self._active_machine.getWorkingProfile())

        #Create regular expression from translated string to prevent (Customised) (Customised) names
        active_profile_name = self._active_profile.getName()
        custom_name_pattern = catalog.i18nc("@item:intext appended to customised profiles ({0} is old profile name)", "{0} (Customised)")
        pattern = re.compile(custom_name_pattern.format(".*?").replace("(", "\(").replace(")", "\)"))
        if not pattern.match(active_profile_name):
            profile.setName(custom_name_pattern.format(active_profile_name))
        else:
            #setName will add "#2" as necessary
            profile.setName(active_profile_name)

        #Make this profile available to all printers of the same type only
        profile.setMachineTypeId(self._active_profile.getMachineTypeId())
        self._profiles.append(profile)
        self.profilesChanged.emit()

        return profile

    def removeProfile(self, profile):
        if profile not in self._profiles:
            return

        self._profiles.remove(profile)
        profile.nameChanged.disconnect(self._onProfileNameChanged)

        path = Resources.getStoragePath(Resources.Profiles, urllib.parse.quote_plus(profile.getName()) + ".cfg")
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

        self.profilesChanged.emit()

        if profile == self._active_profile:
            try:
                self.setActiveProfile(self.getProfiles(instance = self._active_machine)[0])
            except:
                self.setActiveProfile(None)

    def findProfile(self, name, variant_name = None, material_name = None, type_name = None, instance = None):
        profiles = self.getProfiles(type_name = type_name, instance = instance);

        for profile in profiles:
            if profile.getName().lower() == name.lower():
                if (variant_name and not profile.getMachineVariantName() == variant_name) or \
                        (material_name and not profile.getMaterialName() == material_name) or \
                        (type_name and not profile.getType() == type_name):
                    continue
                return profile

        return None

    def makeUniqueProfileName(self, base_name, old_name = None):
        base_name = base_name.strip()
        num_check = re.compile("(.*?)\s*#\d$").match(base_name)
        if(num_check):
            base_name = num_check.group(1)
        if base_name == "":
            base_name = catalog.i18nc("@item:profile name", "Custom profile")
        profile_name = base_name
        i = 1
        #Make sure there is no profile for any instance/variant/material with the same name,
        #except if it is the old name of the same profile we are renaming
        while self.findProfile(profile_name):
            if profile_name == old_name:
                break
            i = i + 1
            profile_name = "%s #%d" % (base_name, i)

        return profile_name

    activeProfileChanged = Signal()

    def getWorkingProfile(self):
        if self._active_machine:
            return self._active_machine.getWorkingProfile()

    def getActiveProfile(self):
        return self._active_profile

    def setActiveProfile(self, profile):
        if profile not in self._profiles or self._active_profile == profile:
            return

        if not self._protect_working_profile:
            working_profile = self._active_machine.getWorkingProfile()
            if working_profile.hasChangedSettings() and not self._confirmReplaceCurrentSettings(profile.getName()):
                return

            #Replace working profile with a copy of the new profile
            working_profile.mergeSettingsFrom(profile, reset = True)

            #Reapply previously selected partial material profile
            if self._active_machine.hasMaterials():
                self.setActiveMaterial(self._active_machine.getMaterialName())

        self._active_profile = profile
        self._active_machine.setActiveProfileName(profile.getName())

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

            for root, dirs, files in os.walk(dir):
                for file_name in files:
                    path = os.path.join(root, file_name)

                    if os.path.isdir(path):
                        continue

                    profile = Profile(self, read_only)
                    try:
                        profile.loadFromFile(path)
                    except Exception as e:
                        Logger.log("e", "An exception occurred loading Profile %s: %s", path, str(e))
                        continue

                    if not self.findProfile(profile.getName(), variant_name = profile.getMachineVariantName(), material_name = profile.getMaterialName(), instance = self._active_machine):
                        self._profiles.append(profile)
                        profile.nameChanged.connect(self._onProfileNameChanged)

        for instance in self._machine_instances:
            try:
                file_name = urllib.parse.quote_plus(instance.getName()) + ".curaprofile"
                instance.getWorkingProfile().loadFromFile(Resources.getStoragePath(Resources.MachineInstanceProfiles, file_name))
            except Exception as e:
                Logger.log("w", "Could not load working profile: %s: %s", file_name, str(e))
                self._setDefaultVariantMaterialProfile(instance)

        self._protect_working_profile = True

        if self._active_machine:
            profile_name = self._active_machine.getActiveProfileName()
            if profile_name == "":
                profile_name = "Normal Quality"

            profile = self.findProfile(self._active_machine.getActiveProfileName(), instance = self._active_machine)
            if profile:
                self.setActiveProfile(profile)
            else:
                profiles = self.getProfiles(instance = self._active_machine)
                if len(profiles) > 0:
                    self.setActiveProfile(profiles[0])

        self.profilesChanged.emit()
        self._protect_working_profile = False

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
            file_name = urllib.parse.quote_plus(instance.getName()) + ".curaprofile"
            instance.getWorkingProfile().saveToFile(Resources.getStoragePath(Resources.MachineInstanceProfiles, file_name))

    def saveProfiles(self):
        try:
            for profile in self._profiles:
                if profile.isReadOnly() or not profile.hasChangedSettings():
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
        file_name = urllib.parse.quote_plus(old_name)
        try:
            path = Resources.getStoragePath(Resources.MachineInstances, file_name + ".cfg")
            os.remove(path)
            path = Resources.getStoragePath(Resources.MachineInstanceProfiles, file_name + ".curaprofile")
            os.remove(path)
        except FileNotFoundError:
            pass

        #Update machine instance name for all profiles attached to this machine instance
        for profile in self._profiles:
            if profile.isReadOnly() or profile.getMachineInstanceName() != old_name:
                continue

            file_name = urllib.parse.quote_plus(profile.getName()) + ".cfg"
            try:
                path = Resources.getStoragePath(Resources.Profiles, file_name)
                os.remove(path)
            except FileNotFoundError:
                pass

            profile.setMachineInstanceName(instance.getName())

        self.machineInstanceNameChanged.emit(instance)

    def _onProfileNameChanged(self, profile, old_name):
        file_name = urllib.parse.quote_plus(old_name) + ".cfg"
        path = Resources.getStoragePath(Resources.Profiles, file_name)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

        self.profileNameChanged.emit(profile)

    def _setDefaultVariantMaterialProfile(self, instance):
        materials = self.getAllMachineMaterials(instance.getName())
        if len(materials) > 0:
            instance.setMaterialName("PLA" if "PLA" in materials else material[0])

        variants = self.getAllMachineVariants(instance.getMachineDefinition().getId())
        for variant in variants:
            if variant.getVariantName() == "0.4 mm":
                instance.setMachineDefinition(variant)
                break

        profile = self.findProfile("Normal Quality", variant_name = instance.getMachineDefinition().getVariantName(), material_name = instance.getMaterialName(), instance = instance)
        if not profile:
            profile = self.findProfile("Normal Quality", material_name = instance.getMaterialName(), instance = instance)
        if not profile:
            profile = self.findProfile("Normal Quality", instance = instance)
        if not profile:
            profiles = self.getProfiles(instance = instance)
            if len(profiles) > 0:
                profile = profiles[0]

        if profile:
            instance.setActiveProfileName(profile.getName())
            if profile.getMaterialName():
                instance.setMaterialName(profile.getMaterialName())

            #Set working profile to a copy of the new profile
            instance.getWorkingProfile().mergeSettingsFrom(profile, reset = True)

            if not profile.getMaterialName() and instance.hasMaterials():
                #Apply partial material profile
                material_profile = self.findProfile(instance.getMaterialName(), type_name = "material", instance = instance)
                instance.getWorkingProfile().mergeSettingsFrom(material_profile, reset = False)

    def _confirmReplaceCurrentSettings(self, selection_name):
        #TODO: Refactor to use a Uranium MessageBox API instead of introducing a dependency on PyQt5
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle(catalog.i18nc("@title:window", "Replace profile"))
        message_box.setText(catalog.i18nc("@label", "Selecting \"{0}\" replaces your current settings.").format(selection_name))

        update_button = None
        create_button = message_box.addButton(catalog.i18nc("@label", "Create profile"), QMessageBox.YesRole)
        discard_button = message_box.addButton(catalog.i18nc("@label", "Discard changes"), QMessageBox.NoRole)
        cancel_button = message_box.addButton(QMessageBox.Cancel)
        if self._active_profile.isReadOnly():
            message_box.setInformativeText(catalog.i18nc("@label", "Do you want to save your settings in a custom profile?"))
        else:
            message_box.setInformativeText(catalog.i18nc("@label", "Do you want to update profile \"{0}\" or save your settings in a new custom profile?".format(self._active_profile.getName())))
            update_button = message_box.addButton(catalog.i18nc("@label", "Update \"{0}\"".format(self._active_profile.getName())), QMessageBox.YesRole)
        message_box.exec_()
        result = message_box.clickedButton()

        if result == cancel_button:
            return False
        elif result == create_button:
            profile = self.addProfileFromWorkingProfile()
            message = UM.Message.Message(catalog.i18nc("@info:status", "Added a new profile named \"{0}\"").format(profile.getName()))
            message.show()
        elif result == update_button:
            #Replace changed settings of the profile with the changed settings of the working profile
            self._active_profile.setChangedSettings(self.getWorkingProfile().getChangedSettings())
        elif result == discard_button:
            pass

        self.getWorkingProfile().setChangedSettings({})
        return True