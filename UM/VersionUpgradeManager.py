# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import collections #For deque, for breadth-first search.
import configparser #To read config files to get the version number from them.
import os #To get the configuration file names and to rename files.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry #To find plug-ins.
from UM.Resources import Resources #To load old versions from.
import UM.Application #To get the name of the application for a message.
import UM.i18n #To translate the "upgrade succeeded" message.
import UM.Message #To show the "upgrade succeeded" message.

catalogue = UM.i18n.i18nCatalog("uranium")

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
    #
    #   \param current_versions For each preference type currently in use, the
    #   current version that is in use.
    def __init__(self, current_versions):
        self._version_upgrades = {} #For each config type and each version, gives a set of upgrade plug-ins that can convert them to something else.
        self._get_version_functions = {} #For each config type, gives a function with which to get the version number from those files.
        self._storage_paths = {} #For each config type, a set of storage paths to search for old config files.
        self._current_versions = current_versions #To know which preference versions and types to upgrade to.

        self._registry = PluginRegistry.getInstance()
        PluginRegistry.addType("version_upgrade", self._addVersionUpgrade)

    ##  Performs the version upgrades of all configuration files to the most
    #   recent version.
    #
    #   The upgrade plug-ins must all be loaded at this point, or no upgrades
    #   can be performed.
    def upgrade(self):
        Logger.log("i", "Looking for old configuration files to upgrade.")
        upgraded = False #Did we upgrade something?
        paths = self._findShortestUpgradePaths()
        for old_configuration_type, storage_paths in self._storage_paths.items():
            for storage_path in storage_paths:
                storage_path_absolute = os.path.relpath(storage_path, Resources.getConfigStoragePath())
                for configuration_file in self._getFilesInDirectory(storage_path_absolute, exclude_paths = ["old"]):
                    configuration_file_absolute = os.path.join(storage_path_absolute, configuration_file)
                    try:
                        with open(configuration_file_absolute) as file_handle:
                            configuration = file_handle.read()
                    except IOError:
                        Logger.log("w", "Can't open configuration file %s for reading.", configuration_file_absolute)
                        continue
                    try:
                        old_version = self._get_version_functions[old_configuration_type](configuration)
                    except: #Version getter gives an exception. Not a valid file. Can't upgrade it then.
                        Logger.log("w", "Invalid %s file: %s", old_configuration_type, configuration_file_absolute)
                        continue
                    version = old_version
                    configuration_type = old_configuration_type
                    while (configuration_type, version) not in self._current_versions:
                        new_type, new_version, upgrade = paths[(configuration_type, version)]
                        try:
                            configuration = upgrade(configuration)
                        except Exception as e:
                            Logger.log("w", "Exception in %s upgrade with %s: %s", old_configuration_type, upgrade.__module__, str(e))
                            break #Continue with next file.
                        version = new_version
                        configuration_type = new_type
                    else: #Upgrade successful (without breaking).
                        if version != old_version:
                            upgraded = True
                            Logger.log("i", "Upgraded %s to version %s.", configuration_file, str(version))
                            self._storeOldFile(storage_path, configuration_file, old_version)
                            try:
                                with open(os.path.join(configuration_file), "a") as file_handle:
                                    file_handle.write(configuration) #Save the new file.
                            except IOError:
                                Logger.log("w", "Couldn't write new configuration file to %s.", configuration_file_absolute)
        if upgraded:
            message = UM.Message(text=catalogue.i18nc("@info:version-upgrade", "A configuration from an older version of {0} was imported.", UM.Application.getInstance().getApplicationName()))
            message.show()

    # private:

    ##  Adds a version upgrade plug-in.
    #
    #   This reads from the metadata which upgrades the plug-in can perform and
    #   sorts the upgrade functions in memory so that the upgrades can be used
    #   when an upgrade is requested.
    #
    #   \param version_upgrade_plugin The plug-in object of the version upgrade
    #   plug-in.
    def _addVersionUpgrade(self, version_upgrade_plugin):
        meta_data = self._registry.getMetaData(version_upgrade_plugin.getPluginId())
        if "version_upgrade" not in meta_data:
            Logger.log("w", "Version upgrade plug-in %s doesn't define any configuration types it can upgrade.", version_upgrade_plugin.getPluginId())
            return #Don't need to add.
        upgrades = self._registry.getMetaData(version_upgrade_plugin.getPluginId())["version_upgrade"]

        for source, destination in upgrades.items(): #Each conversion that this plug-in can perform.
            source_type, source_version, get_version_function = source
            destination_type, destination_version, upgrade_function = destination

            #Fill in the dictionary representing the graph, if it doesn't have the keys yet.
            if (destination_type, destination_version) not in self._version_upgrades:
                self._version_upgrades[(destination_type, destination_version)] = set()
            self._version_upgrades[(destination_type, destination_version)].add((source_type, source_version, upgrade_function, get_version_function)) #Add the edge to the graph.

        #Additional metadata about the source types: How to recognise the version and where to find them.
        if "sources" in meta_data:
            for configuration_type, source in meta_data["sources"].items:
                if "get_version" in source:
                    self._get_version_functions[configuration_type] = source["get_version"] #May overwrite from other plug-ins that can also load the same configuration type.
                if "location" in source:
                    if configuration_type not in self._storage_paths:
                        self._storage_paths[configuration_type] = set()
                    self._storage_paths[configuration_type] |= source["location"]

    ##  Finds the next step to take to upgrade each combination of configuration
    #   type and version.
    #
    #   \return A dictionary of type/version pairs that map to functions that
    #   upgrade said data format one step towards the most recent version, such
    #   that the fewest number of steps is required.
    def _findShortestUpgradePaths(self):
        result = {} #For each (type, version) tuple, which upgrade function to use to upgrade it towards the newest versions.

        #Perform a many-to-many shortest path search with Dijkstra's algorithm.
        front = collections.deque() #Use as a queue for breadth-first iteration: Append right, pop left.
        for configuration_type, version in self._current_versions.items():
            front.append((configuration_type, version))
        explored_versions = set()
        while len(front) > 0:
            destination_type, destination_version = front.popleft() #To make it a queue, pop on the opposite side of where you append!
            if (destination_type, destination_version) in self._version_upgrades: #We can upgrade to this version.
                for source_type, source_version, upgrade_function, _ in self._version_upgrades[(destination_type, destination_version)]:
                    if (source_type, source_version) in explored_versions:
                        continue
                    front.append((source_type, source_version))
                    if (source_type, source_version) not in result: #First time we encounter this version. Due to breadth-first search, this must be part of the shortest path then.
                        result[(source_type, source_version)] = (destination_type, destination_version, upgrade_function)
            explored_versions.add((destination_type, destination_version))

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
    #   \return The filename of each file relative to the specified directory.
    def _getFilesInDirectory(self, directory, exclude_paths = None):
        if not exclude_paths:
            exclude_paths = []
        exclude_paths = [os.path.join(directory, exclude_path) for exclude_path in exclude_paths] # Prepend the specified directory before each exclude path.
        for (path, directory_names, filenames) in os.walk(directory, topdown=True):
            #This variable IS used by os.walk as long as topdown == True.
            #pylint: disable=unused-variable
            directory_names = [directory_name for directory_name in directory_names if os.path.join(path, directory_name) not in exclude_paths] # Prune the exclude paths.
            for filename in filenames:
                yield os.path.join(directory, filename)

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