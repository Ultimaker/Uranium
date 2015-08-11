# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import urllib
import os

from UM.Signal import Signal, SignalEmitter
from UM.Resources import Resources

from UM.Settings.MachineDefinition import MachineDefinition
from UM.Settings.MachineSettings import MachineSettings
from UM.Settings.Profile import Profile
from UM.Settings.SettingsError import SettingsError

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class MachineManager(SignalEmitter):
    def __init__(self):
        super().__init__()

        self._machine_defintions = []
        self._machine_instances = []
        self._profiles = []

        self._active_machine = None
        self._active_profile = None

    machineDefinitionsChanged = Signal()

    def getMachineDefinitions(self):
        return self._machine_defintions

    def getAllMachineVariants(self, machine_id):
        variants = []
        for definition in self._machine_defintions:
            if definition.getId() == machine_id:
                variants.append(definition)

        return variants

    machineInstancesChanged = Signal()

    def getMachineInstance(self, index):
        return self._machine_instances[index]

    def getMachineInstances(self):
        return self._machine_instances

    def addMachineInstance(self, instance):
        if instance in self._machine_instances:
            return

        self._machine_instances.append(instance)
        self.machineInstancesChanged.emit()

    def removeMachineInstance(self, instance):
        if instance not in self._machine_instances:
            return

        self._machine_instances.remove(instance)

        try:
            path = Resources.getStoragePath(Resources.MachineInstances, urllib.parse.quote_plus(instance.getName()) + ".cfg")
            os.remove(path)
        except FileNotFoundError:
            pass

        self.machineInstancesChanged.emit()

    def findMachineInstance(self, name):
        for i in range(len(self._machine_instances)):
            if self._machine_instances[i].getName() == name:
                return i

        return -1

    ##  Get the currently active machine instance
    #   \returns active_machine \type{MachineSettings}
    def getActiveMachineInstance(self):
        return self._active_machine

    ##  Set the currently active machine
    #   \param active_machine \type{MachineSettings}
    def setActiveMachineInstance(self, machine):
        if machine == self._active_machine:
            return

        self._active_machine = machine
        self.activeMachineInstanceChanged.emit()

    activeMachineInstanceChanged = Signal()

    profilesChanged = Signal()

    def getProfiles(self):
        return self._profiles

    def addProfile(self, profile):
        if profile in self._profiles:
            return

        self._profiles.append(profile)
        self.profilesChanged.emit()

    def removeProfile(self, profile):
        if profile not in self._profiles:
            return

        self._profiles.remove(profile)
        self.profilesChanged.emit()

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
        self.activeProfileChanged.emit()

    def loadAll(self):
        self.loadMachineDefinitions()
        self.loadMachineInstances()
        self.loadProfiles()

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

                with open(path, "rt", -1, "utf-8") as f:
                    try:
                        data = json.load(f)
                    except ValueError as e:
                        Logger.log("e", "Error when loading file {0}: {1}".format(path, e))
                        continue

                # Ignore any file that is explicitly marked as non-visible
                if not data.get("visible", True):
                    continue

                # Ignore any file that is marked as non-visible for the current application.
                appname = Application.getInstance().getApplicationName()
                if appname in data:
                    if not data[appname].get("visible", True):
                        continue

                # Ignore files that are reported using an incompatible version
                if "version" not in data or data["version"] != MachineSettings.MachineDefinitionVersion:
                    Logger.log("w", "Machine definition %s uses an incompatible format, ignoring", path)
                    continue

                try:
                    definition = MachineDefinition(data["id"], path)
                except KeyError:
                    Logger.log("e", "JSON file {0} is missing important meta data, ignoring.".format(path))
                    continue

                definition.setName(data.get("name", definition.machine_id))
                definition.setVariantName(data.get("variant_name", None))
                definition.setManufacturer(data.get("manufacturer", catalog.i18nc("", "Other")))
                definition.setAuthor(data.get("author", catalog.i18nc("", "Unknown Author")))
                self._machine_defintions.append(definition)

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

                instance = MachineSettings()
                try:
                    instance.loadFromFile(path)
                except SettingsError as e:
                    Logger.log("w", str(e))
                    continue

                self._machine_instances.append(instance)

        self.machineInstancesChanged.emit()

    def loadProfiles(self):
        dirs = Resources.getAllPathsForType(Resources.Profiles)
        for dir in dirs:
            if not os.path.isdir(dir):
                continue

            for file_name in os.listdir(dir):
                path = os.path.join(dir, file_name)

                if os.path.isdir(path):
                    continue

                profile = Profile()
                try:
                    profile.loadFromFile(path)
                except SettingsError as e:
                    Logger.log("w", str(e))
                    continue

                self._profiles.append(profile)

            #settings_directory = Resources.getStoragePathForType(Resources.Settings)
        #for entry in os.listdir(settings_directory):
            #settings = MachineSettings()
            #settings.loadValuesFromFile(os.path.join(settings_directory, entry))
            #self._machines.append(settings)
        #self._machines.sort(key = lambda k: k.getName())

    ###  Get a list of all machines.
    ##   \returns machines \type{list}s
    #def getMachines(self):
        #return self._machines

    ###  Add a machine to the list.
    ##   The list is sorted by name
    ##   \param machine \type{MachineSettings}
    ##   \returns index \type{int}
    #def addMachine(self, machine):
        #self._machines.append(machine)
        #self._machines.sort(key = lambda k: k.getName())
        #self.machinesChanged.emit()
        #return len(self._machines) - 1

    ###  Remove a machine from the list.
    ##   \param machine \type{MachineSettings}
    #def removeMachine(self, machine):
        #self._machines.remove(machine)

        #try:
            #path = Resources.getStoragePath(Resources.SettingsLocation, urllib.parse.quote_plus(machine.getName()) + ".cfg")
            #os.remove(path)
        #except FileNotFoundError:
            #pass

        #self.machinesChanged.emit()

    #machinesChanged = Signal()
