# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import collections #For deque, for breadth-first search.
import configparser #To read config files to get the version number from them.
import os #To get the configuration file names and to rename files.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry #To find plug-ins.
from UM.Preferences import Preferences #To get the current preferences version.
from UM.Resources import Resources #To load old versions from.
from UM.Settings.MachineInstance import MachineInstance #To get the current machine instance version.
from UM.Settings.Profile import Profile #To get the current profile version.

##  Regulates the upgrading of configuration from one application version to the
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
#   Old versions of the configuration are not deleted, but put in a folder next
#   to the current (upgraded) versions, where they are never loaded again unless
#   the user manually retrieves the files.
class VersionUpgradeManager:
    ##  Initialises the version upgrade manager.
    #
    #   This initialises the cache for shortest upgrade paths, and registers the
    #   version upgrade plug-ins.
    def __init__(self):
        self._versionUpgrades = [] # All upgrade plug-ins.
        self._registry = PluginRegistry.getInstance()
        PluginRegistry.addType("version_upgrade", self._addVersionUpgrade)

    ##  Performs the version upgrades of all configuration files to the most
    #   recent version.
    #
    #   The upgrade plug-ins must all be loaded at this point, or no upgrades
    #   can be performed.
    def upgrade(self):
        self._upgradeConfigurationType(new_version = MachineInstance.MachineInstanceVersion,
                                       configuration_type = "machine_instance",
                                       resource_type = Resources.MachineInstances,
                                       upgrade_method_name = "upgradeMachineInstance",
                                       get_old_version = self._getMachineInstanceVersion)

        self._upgradeConfigurationType(new_version = Preferences.PreferencesVersion,
                                       configuration_type = "preferences",
                                       resource_type = Resources.Preferences,
                                       upgrade_method_name = "upgradePreferences",
                                       get_old_version = self._getPreferencesVersion)

        self._upgradeConfigurationType(new_version = Profile.ProfileVersion,
                                       configuration_type = "profile",
                                       resource_type = Resources.Profiles,
                                       upgrade_method_name = "upgradeProfile",
                                       get_old_version = self._getProfileVersion)

    # private:

    ##  Adds a version upgrade plug-in.
    #
    #   \param version_upgrade_plugin The plug-in object of the version upgrade
    #   plug-in.
    def _addVersionUpgrade(self, version_upgrade_plugin):
        self._versionUpgrades.append(version_upgrade_plugin)

    ##  For each version of a configuration type, finds the next step to take to
    #   upgrade as quickly as possible to the most recent version.
    #
    #   The configuration type should be either "machine_instance",
    #   "preferences" or "profile", matching the types listed in the metadata of
    #   a plug-in. This is abstracted to prevent having to maintain the same
    #   code in lots of different functions that do basically the same.
    #
    #   This function uses a breadth-first search to get the fewest number of
    #   steps required to upgrade to the destination version.
    #
    #   \param configuration_type The type of configuration to compute the
    #   shortest upgrade paths of.
    #   \param destination_version The version to compute the shortest paths to.
    #   \return A dictionary with an entry for each version number from which we
    #   can reach the destination version, naming the version upgrade plug-in
    #   with which to convert for the next step.
    def _findShortestUpgradePaths(self, configuration_type, destination_version):
        by_destination_version = self._sortByDestinationVersion(configuration_type)
        result = {}

        # Perform a breadth-first search.
        registry = PluginRegistry.getInstance()
        front = collections.deque() # Use as a queue for breadth-first iteration: Append right, pop left.
        front.append(destination_version)
        explored_versions = set()
        while len(front) > 0:
            version = front.popleft() # To make it a queue, pop on the opposite side of where you append!
            if version in by_destination_version: # We can upgrade to this version.
                for neighbour in by_destination_version[version]:
                    source_version = registry.getMetaData(neighbour.getPluginId())["version_upgrade"][configuration_type]["from"]
                    if source_version in explored_versions: # Already encountered elsewhere. No need to re-compute.
                        continue
                    front.append(source_version)
                    if source_version not in result: # First time we encounter this version. Due to breadth-first search, this must be part of the shortest path then.
                        result[source_version] = neighbour
            explored_versions.add(version)

        return result

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
        exclude_paths = [os.path.join(directory, exclude_path) for exclude_path in exclude_paths] # Prepend the specified directory before each exclude path.
        for (path, directory_names, filenames) in os.walk(directory):
            directory_names = [directory_name for directory_name in directory_names if os.path.join(path, directory_name) not in exclude_paths] # Prune the exclude paths.
            for filename in filenames:
                yield os.path.join(os.path.relpath(path, directory), filename)

    ##  Gets the version of a machine instance file.
    #
    #   \param machine_instance The contents of a machine_instance file.
    #   \return The version of the machine instance.
    def _getMachineInstanceVersion(self, machine_instance):
        return int(self._getCfgItem(machine_instance, section = "general", item = "version"))

    ##  Gets the version of a preferences file.
    #
    #   \param preferences The contents of a preferences file.
    #   \return The version of the preferences.
    def _getPreferencesVersion(self, preferences):
        return int(self._getCfgItem(preferences, section = "general", item = "version"))

    ##  Gets the version of a profile file.
    #
    #   \param profile The contents of a profile file.
    #   \return The version of the profile.
    def _getProfileVersion(self, profile):
        return int(self._getCfgItem(profile, section = "general", item = "version"))

    ##  Creates a look-up table to get plug-ins by what version they upgrade
    #   to.
    #
    #   \param configuration_type The type of configuration file the version
    #   number applies to.
    #   \return A dictionary with an entry for every version that the upgrade
    #   plug-ins can convert to, and which plug-ins can convert to that version.
    def _sortByDestinationVersion(self, configuration_type):
        result = {}
        for plugin in self._versionUpgrades:
            metadata = self._registry.getMetaData(plugin.getPluginId())["version_upgrade"]
            if configuration_type not in metadata: # Filter by configuration_type.
                continue
            destination = metadata[configuration_type]["to"]
            if not destination in result: # Entry doesn't exist yet.
                result[destination] = []
            result[destination].append(plugin) # Sort this plug-in under the correct entry.
        return result

    ##  Stores an old version of a configuration file away.
    #
    #   This old file is intended as a back-up. It will be stored in the ./old
    #   directory in the resource directory, in a subdirectory made specifically
    #   for the version of the old file. The subdirectory will mirror the
    #   directory structure of the original directory.
    #
    #   \param resource_directory The resource directory of the configuration
    #   type of the file in question.
    #   \param relative_path The path relative to the resource directory to the
    #   file in question.
    #   \param old_version The version number in the file in question.
    def _storeOldFile(self, resource_directory, relative_path, old_version):
        try: # For speed, first just try to rename the file without checking if the directory exists and stuff.
            os.rename(os.path.join(resource_directory,                          relative_path),
                      os.path.join(resource_directory, "old", str(old_version), relative_path)) # Store the old file away.
        except FileNotFoundError: # Assume the target directory doesn't exist yet. The other case is that the file itself doesn't exist, but that's a coding error anyway.
            try:
                os.makedirs(os.path.join(resource_directory, "old", str(old_version)))
            except OSError: # Assume that the directory already existed. Otherwise it's probably a permission error or OS-internal error, in which case we can't write anyway.
                pass
            os.rename(os.path.join(resource_directory,                          relative_path),
                      os.path.join(resource_directory, "old", str(old_version), relative_path)) # Try again!

    ##  Performs the upgrade process of a single configuration type.
    #
    #   \param new_version The version to upgrade to.
    #   \param configuration_type The configuration type to upgrade, as
    #   specified by the upgrade plug-ins.
    #   \param resource_type The resource type of the files to upgrade. This is
    #   required to know where the configuration files are stored.
    #   \param upgrade_function_name The name of the method to upgrade the file
    #   with. This is the name of the function that is called on the version
    #   upgrade plug-in.
    #   \param get_old_version A function pointer to indicate how to get the
    #   version number of this file.
    def _upgradeConfigurationType(self, new_version, configuration_type, resource_type, upgrade_method_name, get_old_version):
        paths = self._findShortestUpgradePaths(configuration_type, new_version)
        base_directory = Resources.getStoragePathForType(resource_type)
        for configuration_file in self._getFilesInDirectory(base_directory, exclude_paths = ["old"]):
            with open(os.path.join(base_directory, configuration_file)) as file_handle:
                configuration = file_handle.read()
            try:
                old_version = get_old_version(configuration)
            except: # Not a valid file. Can't upgrade it then.
                Logger.log("w", "Invalid %s file: %s", configuration_type, configuration_file)
                continue
            if old_version not in paths: # No upgrade to bring this up to the most recent version.
                continue
            version = old_version
            while version != new_version:
                upgrade = paths[version] # Get the upgrade to apply from this place.
                try:
                    configuration = getattr(upgrade, upgrade_method_name)(configuration) # Do the actual upgrade.
                except Exception as e:
                    Logger.log("w", "Exception in " + configuration_type + " upgrade with " + upgrade.getPluginId() + ": " + str(e))
                    break # Continue with next file.
                version = self._registry.getMetaData(upgrade.getPluginId())["version_upgrade"][configuration_type]["to"]
            else:
                if version != old_version:
                    self._storeOldFile(base_directory, configuration_file, old_version)
                    with open(os.path.join(base_directory, configuration_file), "a") as file_handle:
                        file_handle.write(configuration) # Save the new file.