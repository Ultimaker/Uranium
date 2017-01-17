# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import collections #For deque, for breadth-first search and to track tasks, and namedtuple.
import os #To get the configuration file names and to rename files.
import traceback

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry #To find plug-ins.
from UM.Resources import Resources #To load old versions from.
import UM.Application #To get the name of the application for a message.
import UM.i18n #To translate the "upgrade succeeded" message.
import UM.Message #To show the "upgrade succeeded" message.
import UM.MimeTypeDatabase #To know how to save the resulting files.

catalogue = UM.i18n.i18nCatalog("uranium")

##  File that needs upgrading, with all the required info to upgrade it.
#
#   Fields are:
#   - storage_path: A path to where the type of file is stored before upgrading.
#     This is used to store the old file in an /old directory.
#   - file_name: The name to the file that needs to be upgraded, relative to the
#     storage path.
#   - configuration_type: The configuration type of the file before upgrading.
UpgradeTask = collections.namedtuple("UpgradeTask", ["storage_path", "file_name", "configuration_type"])

##  Regulates the upgrading of configuration from one application version to the
#   next.
#
#   The process of upgrading will take a look at all profiles, preferences and
#   machine instances and check their version numbers. If they are older than
#   the current version number of their respective type of file, an upgrade
#   route will be planned for it in order to upgrade the file to the current
#   version in as few conversions as possible.
#
#   To this end, the upgrade manager will maintain the shortest routes to the
#   current version for each of the types of profiles and each old version it
#   encounters. Once a shortest route is found, it is cached and can be re-used
#   for all nodes along this route. This minimises the extra start-up time
#   required for the conversions.
#
#   Old versions of the configuration are not deleted, but put in a folder next
#   to the current (upgraded) versions, where they are never loaded again unless
#   the user manually retrieves the files.
class VersionUpgradeManager:
    ##  The singleton instance of this class.
    __instance = None

    ##  Gets the instance of the VersionUpgradeManager, or creates one.
    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = VersionUpgradeManager()
        return cls.__instance

    ##  Initialises the version upgrade manager.
    #
    #   This initialises the cache for shortest upgrade routes, and registers
    #   the version upgrade plug-ins.
    def __init__(self):
        self._version_upgrades = {} #For each config type and each version, gives a set of upgrade plug-ins that can convert them to something else.
        self._get_version_functions = {} #For each config type, gives a function with which to get the version number from those files.
        self._storage_paths = {} #For each config type, a set of storage paths to search for old config files.
        self._current_versions = {} #To know which preference versions and types to upgrade to.
        self._upgrade_tasks = collections.deque() #The files that we still have to upgrade.
        self._upgrade_routes = {} #How to upgrade from one version to another. Needs to be pre-computed after all version upgrade plug-ins are registered.

        self._registry = PluginRegistry.getInstance()
        PluginRegistry.addType("version_upgrade", self._addVersionUpgrade)

    ##  Gets the paths where a specified type of file should be stored.
    #
    #   This differs from the storage path in the Resources class, since it also
    #   knows where to store old file types. This information is gathered from
    #   the upgrade plug-ins.
    #
    #   \param configuration_type The type of configuration to be stored.
    #   \return A set of storage paths for the specified configuration type.
    def getStoragePaths(self, configuration_type):
        return self._storage_paths[configuration_type]

    ##  Changes the target versions to upgrade to.
    #
    #   \param current_versions A dictionary of tuples of configuration types
    #   and their versions currently in use, and with each of these a tuple of
    #   where to store this type of file and its MIME type.
    def setCurrentVersions(self, current_versions):
        self._current_versions = current_versions

    ##  Performs the version upgrades of all configuration files to the most
    #   recent version.
    #
    #   The upgrade plug-ins must all be loaded at this point, or no upgrades
    #   can be performed.
    #
    #   \return True if anything was upgraded, or False if it was already up to
    #   date.
    def upgrade(self):
        Logger.log("i", "Looking for old configuration files to upgrade.")
        self._upgrade_tasks.extend(self._getUpgradeTasks())     #Get the initial files to upgrade.
        self._upgrade_routes = self._findShortestUpgradeRoutes() #Pre-compute the upgrade routes.

        upgraded = False #Did we upgrade something?
        while self._upgrade_tasks:
            upgrade_task = self._upgrade_tasks.popleft()
            self._upgradeFile(upgrade_task.storage_path, upgrade_task.file_name, upgrade_task.configuration_type) #Upgrade this file.

        if upgraded:
            message = UM.Message(text=catalogue.i18nc("@info:version-upgrade", "A configuration from an older version of {0} was imported.", UM.Application.getInstance().getApplicationName()))
            message.show()
        return upgraded

    ##  Schedules an additional file for upgrading.
    #
    #   This method is intended to be called by upgrade plug-ins during
    #   upgrading, to make sure we also upgrade any extra files that should be
    #   added during the upgrade process.
    #   Note that the file is not immediately upgraded, but scheduled for
    #   upgrading. If this method is called while the ``upgrade()`` function is
    #   still running, it will get upgraded at the end of that run. If it is
    #   called while the ``upgrade()`` function is not running, it would get
    #   upgraded during the next call to ``upgrade()``.
    #
    #   \param storage_path The path to where the specified type of file is
    #   stored.
    #   \param file_name The path to the file to upgrade, relative to the
    #   storage path.
    #   \param configuration_type The file type of the specified file.
    def upgradeExtraFile(self, storage_path, file_name, configuration_type):
        self._upgrade_tasks.append(UpgradeTask(storage_path = storage_path, file_name = file_name, configuration_type = configuration_type))

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

        #Additional metadata about the source types: How to recognise the version and where to find them.
        if "sources" in meta_data:
            for configuration_type, source in meta_data["sources"].items():
                if "get_version" in source:
                    self._get_version_functions[configuration_type] = source["get_version"] #May overwrite from other plug-ins that can also load the same configuration type.
                if "location" in source:
                    if configuration_type not in self._storage_paths:
                        self._storage_paths[configuration_type] = set()
                    self._storage_paths[configuration_type] |= source["location"]

        upgrades = self._registry.getMetaData(version_upgrade_plugin.getPluginId())["version_upgrade"]
        for source, destination in upgrades.items(): #Each conversion that this plug-in can perform.
            source_type, source_version = source
            destination_type, destination_version, upgrade_function = destination

            #Fill in the dictionary representing the graph, if it doesn't have the keys yet.
            if (destination_type, destination_version) not in self._version_upgrades:
                self._version_upgrades[(destination_type, destination_version)] = set()
            self._version_upgrades[(destination_type, destination_version)].add((source_type, source_version, upgrade_function)) #Add the edge to the graph.

    ##  Finds the next step to take to upgrade each combination of configuration
    #   type and version.
    #
    #   \return A dictionary of type/version pairs that map to functions that
    #   upgrade said data format one step towards the most recent version, such
    #   that the fewest number of steps is required.
    def _findShortestUpgradeRoutes(self):
        result = {} #For each (type, version) tuple, which upgrade function to use to upgrade it towards the newest versions.

        #Perform a many-to-many shortest path search with Dijkstra's algorithm.
        front = collections.deque() #Use as a queue for breadth-first iteration: Append right, pop left.
        for configuration_type, version in self._current_versions:
            front.append((configuration_type, version))
        explored_versions = set()
        while len(front) > 0:
            destination_type, destination_version = front.popleft() #To make it a queue, pop on the opposite side of where you append!
            if (destination_type, destination_version) in self._version_upgrades: #We can upgrade to this version.
                for source_type, source_version, upgrade_function in self._version_upgrades[(destination_type, destination_version)]:
                    if (source_type, source_version) in explored_versions:
                        continue
                    front.append((source_type, source_version))
                    if (source_type, source_version) not in result: #First time we encounter this version. Due to breadth-first search, this must be part of the shortest route then.
                        result[(source_type, source_version)] = (destination_type, destination_version, upgrade_function)
            explored_versions.add((destination_type, destination_version))

        return result

    ##  Get the filenames of all files in a specified directory.
    #
    #   If an exclude path is given, the specified path is ignored (relative to
    #   the specified directory).
    #
    #   \param directory The directory to read the files from.
    #   \return The filename of each file relative to the specified directory.
    def _getFilesInDirectory(self, directory):
        result = []
        for (path, directory_names, filenames) in os.walk(directory, topdown=True):
            directory_names[:] = [] # Only go to one level.
            for filename in filenames:
                relative_path = os.path.relpath(path, directory)
                result.append(os.path.join(relative_path, filename))
        return result

    ##  Gets all files that need to be upgraded.
    #
    #   \return A list of UpgradeTasks of files to upgrade.
    def _getUpgradeTasks(self):
        result = []
        storage_path_prefixes = set()
        storage_path_prefixes.add(Resources.getConfigStoragePath())
        for old_configuration_type, storage_paths in self._storage_paths.items():
            for prefix in storage_path_prefixes:
                for storage_path in storage_paths:
                    path = os.path.join(prefix, storage_path)
                    for configuration_file in self._getFilesInDirectory(path):
                        result.append(UpgradeTask(storage_path = path, file_name = configuration_file, configuration_type = old_configuration_type))
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
        newpath = os.path.join(resource_directory, "old", str(old_version), relative_path)
        if os.path.exists(newpath): #If we've updated previously but this old version was launched again, overwrite the old configuration.
            try:
                os.remove(newpath)
            except OSError: #Couldn't remove. Permissions?
                return
        try: #For speed, first just try to rename the file without checking if the directory exists and stuff.
            os.rename(os.path.join(resource_directory, relative_path), newpath) #Store the old file away.
        except FileNotFoundError: #Assume the target directory doesn't exist yet. The other case is that the file itself doesn't exist, but that's a coding error anyway.
            try:
                os.makedirs(os.path.join(resource_directory, "old", str(old_version)))
            except OSError: #Assume that the directory already existed. Otherwise it's probably a permission error or OS-internal error, in which case we can't write anyway.
                pass
            try:
                os.rename(os.path.join(resource_directory, relative_path), newpath) #Try again!
            except FileExistsError: #Couldn't remove the old file for some other reason. Internal OS error?
                pass
        except FileExistsError:
            pass

    ##  Upgrades a single file to any version in self._current_versions.
    #
    #   A single file will be taken as source file, but may result in any number
    #   of output files.
    #
    #   \param storage_path_absolute The path where to find the file.
    #   \param configuration_file The file to upgrade to a current version.
    #   \param old_configuration_type The type of the configuration file before
    #   upgrading it.
    #   \return True if the file was successfully upgraded, or False otherwise.
    def _upgradeFile(self, storage_path_absolute, configuration_file, old_configuration_type):
        configuration_file_absolute = os.path.join(storage_path_absolute, configuration_file)

        #Read the old file.
        try:
            with open(configuration_file_absolute, encoding = "utf-8", errors = "ignore") as file_handle:
                files_data = [file_handle.read()]
        except MemoryError: #File is too big. It might be the log.
            return False
        except FileNotFoundError: #File was already moved to an /old directory.
            return False
        except IOError:
            Logger.log("w", "Can't open configuration file %s for reading.", configuration_file_absolute)
            return False

        #Get the version number of the old file.
        try:
            old_version = self._get_version_functions[old_configuration_type](files_data[0])
        except: #Version getter gives an exception. Not a valid file. Can't upgrade it then.
            return False
        version = old_version
        configuration_type = old_configuration_type

        try:
            mime_type = UM.MimeTypeDatabase.getMimeTypeForFile(configuration_file)  # Get the actual MIME type object, from the name.
        except UM.MimeTypeDatabase.MimeTypeNotFoundError:
            return False

        filenames_without_extension = [self._stripMimeTypeExtension(mime_type, configuration_file)]

        #Keep converting the file until it's at one of the current versions.
        while (configuration_type, version) not in self._current_versions:
            if (configuration_type, version) not in self._upgrade_routes:
                #No version upgrade plug-in claims to be able to upgrade this file.
                return False
            new_type, new_version, upgrade_step = self._upgrade_routes[(configuration_type, version)]
            new_filenames_without_extension = []
            new_files_data = []
            for file_idx, file_data in enumerate(files_data):
                try:
                    this_filenames_without_extension, this_files_data = upgrade_step(file_data, filenames_without_extension[file_idx])
                except Exception as e: #Upgrade failed due to a coding error in the plug-in.
                    Logger.logException("w", "Exception in %s upgrade with %s: %s", old_configuration_type,
                                        upgrade_step.__module__, traceback.format_exc() )
                    return False
                if not this_files_data: #Upgrade failed.
                    Logger.log("w", "Unable to upgrade the file %s. Skipping it.", filenames_without_extension[file_idx])
                    return False
                new_filenames_without_extension += this_filenames_without_extension
                new_files_data += this_files_data
            filenames_without_extension = new_filenames_without_extension
            files_data = new_files_data
            version = new_version
            configuration_type = new_type

        #If the version changed, save the new files.
        if version != old_version or configuration_type != old_configuration_type:
            self._storeOldFile(storage_path_absolute, configuration_file, old_version)

            #Finding out where to store these files.
            resource_type, mime_type = self._current_versions[(configuration_type, version)]
            storage_path = Resources.getStoragePathForType(resource_type)
            mime_type = UM.MimeTypeDatabase.getMimeType(mime_type) #Get the actual MIME type object, from the name.
            if mime_type.preferredSuffix:
                extension = "." + mime_type.preferredSuffix
            elif mime_type.suffixes:
                extension = "." + mime_type.suffixes[0]
            else:
                extension = "" #No known suffix. Put no extension behind it.
            new_filenames = [filename + extension for filename in filenames_without_extension]
            configuration_files_absolute = [os.path.join(storage_path, filename) for filename in new_filenames]

            for file_idx, configuration_file_absolute in enumerate(configuration_files_absolute):
                try:
                    with open(os.path.join(configuration_file_absolute), "w", encoding = "utf-8") as file_handle:
                        file_handle.write(files_data[file_idx]) #Save the new file.
                except IOError:
                    Logger.log("w", "Couldn't write new configuration file to %s.", configuration_file_absolute)
                    return False
            Logger.log("i", "Upgraded %s to version %s.", configuration_file, str(version))
            return True
        return False #Version didn't change. Was already current.

    def _stripMimeTypeExtension(self, mime_type, file_name):
        suffixes = mime_type.suffixes[:]
        if mime_type.preferredSuffix:
            suffixes.append(mime_type.preferredSuffix)
        for suffix in suffixes:
            if file_name.endswith(suffix):
                return file_name[: -len(suffix) -1] # last -1 is for the dot separating name and extension.

        return file_name
