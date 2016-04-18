# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.PluginRegistry import PluginRegistry #To find plug-ins.
from UM.Preferences import Preferences #To get the current preferences version.
from UM.Resources import Resources #To load old versions from.
from UM.Settings.MachineInstance import MachineInstance #To get the current machine instance version.
from UM.Settings.Profile import Profile #To get the current profile version.

import collections #For deque, for breadth-first search.
import configparser #To read config files to get the version number from them.
import os #To get the setting filenames.

##  Regulates the upgrading of preferences from one application version to the
#   next.
#
#   The process of upgrading will take a look at all profiles, preferences and
#   machine instances and check their version numbers. If they are older than
#   the current version number of their respective type of file, an upgrade path
#   will be planned for it in order to upgrade the file to the current version
#   in as few conversions as possible.
#
#   To this end, the upgrade manager will maintain the shortest paths to the
#   current version for each of the types of profiles and each old version it
#   encounters. Once a shortest path is found, it is cached and can be re-used
#   for all nodes along this path. This minimises the extra start-up time
#   required for the conversions.
#
#   Old versions of the preferences are not deleted, but put in a folder next to
#   the current (upgraded) versions, where they are never loaded again unless
#   the user manually retrieves the files.
class VersionUpgradeManager:
    ##  Initialises the version upgrade manager.
    #
    #   This initialises the cache for shortest upgrade paths, and registers the
    #   version upgrade plug-ins.
    def __init__(self):
        #Initialise the caches for shortest upgrade paths.
        #These dictionaries are keyed by the version number for which it is the shortest path.
        #The value indicates the version upgrade plug-in to use to upgrade to the next version.
        self._machine_instance_upgrade_paths = {} #The shortest paths to upgrade machine instances to the current version.
        self._preferences_upgrade_paths = {} #The shortest paths to upgrade preferences to the current version.
        self._profile_upgrade_paths = {} #The shortest paths to upgrade profiles to the current version.

        self._versionUpgrades = [] #All upgrade plug-ins.
        PluginRegistry.addType("version_upgrade", self._addVersionUpgrade)

    ##  Performs the version upgrades of all preference files to the most recent
    #   version.
    #
    #   The upgrade plug-ins must all be loaded at this point, or no upgrades
    #   can be performed.
    def upgrade(self):
        registry = PluginRegistry.getInstance()

        paths = self._findShortestUpgradePaths("machine_instance", MachineInstance.MachineInstanceVersion)
        for machine_instance_file in self._getFilesInDirectory(Resources.getStoragePath(Resources.MachineInstances), exclude_paths = ["old"]):
            with file(machine_instance_file) as file_handle:
                machine_instance = file_handle.read()
            try:
                version = self._getMachineInstanceVersion(machine_instance)
            except: #Not a valid file. Can't upgrade it then.
                continue
            if version not in paths: #No upgrade to bring this up to the most recent version.
                continue
            while version != MachineInstance.MachineInstanceVersion:
                upgrade = paths[version] #Get the upgrade to apply from this place.
                machine_instance = upgrade.upgradeMachineInstance(machine_instance) #Do the actual upgrade.
                version = registry.getMetaData(upgrade.getPluginId())["version_upgrade"]["machine_instance"]["to"]

        paths = self._findShortestUpgradePaths("preferences", Preferences.PreferencesVersion)
        for preferences_file in self._getFilesInDirectory(Resources.getStoragePath(Resources.Preferences), exclude_paths = ["old"]):
            with file(preferences_file) as file_handle:
                preferences = file_handle.read()
            try:
                version = self._getPreferencesVersion(preferences)
            except: #Not a valid file. Can't upgrade it then.
                continue
            if version not in paths: #No upgrade to bring this up to the most recent version.
                continue
            while version != Preferences.PreferencesVersion:
                upgrade = paths[version] #Get the upgrade to apply from this place.
                preferences = upgrade.upgradePreferences(preferences) #Do the actual upgrade.
                version = registry.getMetaData(upgrade.getPluginId())["version_upgrade"]["preferences"]["to"]

        paths = self._findShortestUpgradePaths("profile", Profile.ProfileVersion)
        for profile_file in self._getFilesInDirectory(Resources.getStoragePath(Resources.Profiles), exclude_paths = ["old"]):
            with file(profile_file) as file_handle:
                profile = file_handle.read()
            try:
                version = self._getProfileVersion(profile)
            except: #Not a valid file. Can't upgrade it then.
                continue
            if version not in paths: #No upgrade to bring this up to the most recent version.
                continue
            while version != Profile.ProfileVersion:
                upgrade = paths[version] #Get the upgrade to apply from this place.
                profile = upgrade.upgradeProfile(profile) #Do the actual upgrade.
                version = registry.getMetaData(upgrade.getPluginId())["version_upgrade"]["profile"]["to"]

    # private:

    ##  Adds a version upgrade plug-in.
    #
    #   \param version_upgrade_plugin The plug-in object of the version upgrade
    #   plug-in.
    def _addVersionUpgrade(self, version_upgrade_plugin):
        self._versionUpgrades.append(version_upgrade_plugin)

    ##  Gets a single item out of a config file.
    #
    #   This uses the config parser to read the entire file, then gets the
    #   requested property from it. That makes it hella inefficient! But if you
    #   only need one item, it is convenient to use this function.
    #
    #   This function does not do any error checking. If the config file is not
    #   well-formed, an exception will be raised.
    #
    #   \param config_file The contents of a config file.
    #   \param section The section to get the item from.
    #   \param item The item to read from the specified section.
    #   \return The value of the specified item, as a string.
    def _getCfgItem(self, config_file, section, item):
        config = configparser.ConfigParser(interpolation = None)
        config.read_string(config_file)
        return config.get(section, item)

    ##  Gets the version of a machine instance file.
    #
    #   \param machine_instance The contents of a machine_instance file.
    #   \return The version of the machine instance.
    def _getMachineInstanceVersion(self, machine_instance):
        return self._getCfgItem(machine_instance, section = "general", item = "version")

    ##  Gets the version of a preferences file.
    #
    #   \param preferences The contents of a preferences file.
    #   \return The version of the preferences.
    def _getPreferencesVersion(self, preferences):
        return self._getCfgItem(preferences, section = "general", item = "version")

    ##  Gets the version of a profile file.
    #
    #   \param profile The contents of a profile file.
    #   \return The version of the profile.
    def _getProfileVersion(self, profile):
        return self._getCfgItem(profile, section = "general", item = "version")

    ##  For each version of a preference type, finds the next step to take to
    #   upgrade as quickly as possible to the most recent version.
    #
    #   The preference type should be either "machine_instance", "preferences"
    #   or "profile", matching the types listed in the metadata of a plug-in.
    #   This is abstracted to prevent having to maintain the same code in lots
    #   of different functions that do basically the same.
    #
    #   This function uses a breadth-first search to get the fewest number of
    #   steps required to upgrade to the destination version.
    #
    #   \param preference_type The type of preference to compute the shortest
    #   upgrade paths of.
    #   \param destination_version The version to compute the shortest paths to.
    #   \return A dictionary with an entry for each version number from which we
    #   can reach the destination version, naming the version upgrade plug-in
    #   with which to convert for the next step.
    def _findShortestUpgradePaths(self, preference_type, destination_version):
        by_destination_version = self._sortByDestinationVersion(preference_type)
        result = {}

        #Perform a breadth-first search.
        registry = PluginRegistry.getInstance()
        front = collections.deque() #Use as a queue for breadth-first iteration: Append right, pop left.
        front.append(destination_version)
        done = set() #Flag explored versions as done.
        while len(front) > 0:
            version = front.popleft() #To make it a queue, pop on the opposite side of where you append!
            if version in by_destination_version: #We can upgrade to this version.
                for neighbour in by_destination_version[version]:
                    source_version = registry.getMetaData(neighbour.getPluginId())["version_upgrade"][preference_type]["from"]
                    if source_version in done: #Already encountered elsewhere. No need to re-compute.
                        continue
                    front.append(source_version)
                    if source_version not in result: #First time we encounter this version. Due to breadth-first search, this must be part of the shortest path then.
                        result[source_version] = neighbour
            done.add(version)

        return result

    ##  Get the filenames of all files in a specified directory and its
    #   subdirectories.
    #
    #   If an exclude path is given, the specified path is ignored (relative to
    #   the specified directory).
    #
    #   \param directory The directory to read the files from.
    #   \param exclude_paths (Optional) A list of paths, relative to the
    #   specified directory, to directories which must be excluded from the
    #   result.
    #   \return The filename of each file in the specified directory.
    def _getFilesInDirectory(self, directory, exclude_paths = []):
        exclude_paths = [os.path.join(directory, exclude_path) for exclude_path in exclude_paths] #Prepend the specified directory before each exclude path.
        for (path, directory_names, filenames) in os.walk(directory):
            directory_names[:] = [directory_name for directory_name in directory_names if os.path.join(path, directory_name) not in exclude_paths] #Prune the exclude paths.
            for filename in filenames:
                yield filename

    ##  Creates a look-up table to get plug-ins by what version they upgrade
    #   to.
    #
    #   \param preference_type The type of preference file the version number
    #   applies to.
    #   \return A dictionary with an entry for every version that the upgrade
    #   plug-ins can convert to, and which plug-ins can convert to that version.
    def _sortByDestinationVersion(self, preference_type):
        result = {}
        registry = PluginRegistry.getInstance()
        for plugin in self._versionUpgrades:
            metadata = registry.getMetaData(plugin.getPluginId())["version_upgrade"]
            if preference_type not in metadata: #Filter by preference_type.
                continue
            destination = metadata[preference_type]["to"]
            if not destination in result: #Entry doesn't exist yet.
                result[destination] = []
            result[destination].append(plugin) #Sort this plug-in under the correct entry.
        return result