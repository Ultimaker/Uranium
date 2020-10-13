# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import collections  # For deque, for breadth-first search and to track tasks, and namedtuple.
import os  # To get the configuration file names and to rename files.
import re
import traceback
import time
from typing import Any, Dict, Callable, Iterator, List, Optional, Set, Tuple

import UM.Message  # To show the "upgrade succeeded" message.
import UM.MimeTypeDatabase  # To know how to save the resulting files.
import UM.i18n  # To translate the "upgrade succeeded" message.
from UM.Application import Application
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeType
from UM.PluginObject import PluginObject
from UM.PluginRegistry import PluginRegistry  # To find plug-ins.
from UM.Resources import Resources  # To load old versions from.

from PyQt5.QtCore import QCoreApplication

from UM.SaveFile import SaveFile

catalogue = UM.i18n.i18nCatalog("uranium")

UpgradeTask = collections.namedtuple("UpgradeTask", ["storage_path", "file_name", "configuration_type"])
"""File that needs upgrading, with all the required info to upgrade it.

   Fields are:

   - storage_path: A path to where the type of file is stored before upgrading.
                   This is used to store the old file in an /old directory.
   - file_name: The name to the file that needs to be upgraded, relative to the
                storage path.
   - configuration_type: The configuration type of the file before upgrading.
"""

FilesDataUpdateResult = collections.namedtuple("FilesDataUpdateResult",
                                               ["configuration_type", "version", "files_data",
                                                "file_names_without_extension"])


class VersionUpgradeManager:
    """Regulates the upgrading of configuration from one application version to the
    next.

    The process of upgrading will take a look at all profiles, preferences and
    machine instances and check their version numbers. If they are older than
    the current version number of their respective type of file, an upgrade
    route will be planned for it in order to upgrade the file to the current
    version in as few conversions as possible.

    To this end, the upgrade manager will maintain the shortest routes to the
    current version for each of the types of profiles and each old version it
    encounters. Once a shortest route is found, it is cached and can be re-used
    for all nodes along this route. This minimises the extra start-up time
    required for the conversions.

    Old versions of the configuration are not deleted, but put in a folder next
    to the current (upgraded) versions, where they are never loaded again unless
    the user manually retrieves the files.
    """

    def __init__(self, application: Application) -> None:
        """Initialises the version upgrade manager.

        This initialises the cache for shortest upgrade routes, and registers
        the version upgrade plug-ins.
        """

        if VersionUpgradeManager.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        VersionUpgradeManager.__instance = self

        super().__init__()

        self._application = application
        self._version_upgrades = {} # type: Dict[Tuple[str, int], Set[Tuple[str, int, Callable[[str, str], Optional[Tuple[List[str], List[str]]]]]]]   # For each config type and each version, gives a set of upgrade plug-ins that can convert them to something else.

        # For each config type, gives a function with which to get the version number from those files.
        self._get_version_functions = {}  # type: Dict[str, Callable[[str], int]]

        # For each config type, a set of storage paths to search for old config files.
        self._storage_paths = {}  # type: Dict[str, Dict[int, Set[str]]]

        # To know which preference versions and types to upgrade to.
        self._current_versions = {} # type: Dict[Tuple[str, int], Any]

        self._upgrade_tasks = collections.deque()  # type: collections.deque  # The files that we still have to upgrade.
        self._upgrade_routes = {}  # type: Dict[Tuple[str, int], Tuple[str, int, Callable[[str, str], Optional[Tuple[List[str], List[str]]]]]] #How to upgrade from one version to another. Needs to be pre-computed after all version upgrade plug-ins are registered.

        self._registry = PluginRegistry.getInstance()   # type: PluginRegistry
        PluginRegistry.addType("version_upgrade", self._addVersionUpgrade)

        #Regular expressions of the files that should not be checked, such as log files.
        self._ignored_files = [
            ".*\.lock",       # Don't upgrade the configuration file lock. It's not persistent.
            "plugins\.json",  # plugins.json and packages.json need to remain the same for the version upgrade plug-ins.
            "packages\.json",
            ".*\.log",        # Don't process the log. It's not needed and it could be really big.
            ".*\.log.?",      # Don't process the backup of the log. It's not needed and it could be really big.
            "3.[0-3]\\.*",    # Don't upgrade folders that are back-ups from older version upgrades. Until v3.3 we stored the back-up in the config folder itself.
            "3.[0-3]/.*",
            "2.[0-7]\\.*",
            "2.[0-7]/.*",
            "cura\\.*",
            "cura/.*",
            "plugins\\.*",    # Don't upgrade manually installed plug-ins.
            "plugins/.*",
            "./*packages\.json",
            "./*plugins\.json"
        ]  # type: List[str]

    def registerIgnoredFile(self, file_name: str) -> None:
        """Registers a file to be ignored by version upgrade checks (eg log files).

        :param file_name: The base file name of the file to be ignored.
        """

        # Convert the file name to a regular expresion to add to the ignored files
        file_name_regex = re.escape(file_name)
        self._ignored_files.append(file_name_regex)

    def getStoragePaths(self, configuration_type: str) -> Dict[int, Set[str]]:
        """Gets the paths where a specified type of file should be stored.

        This differs from the storage path in the Resources class, since it also
        knows where to store old file types. This information is gathered from
        the upgrade plug-ins.

        :param configuration_type: The type of configuration to be stored.
        :return: A set of storage paths for the specified configuration type.
        """

        return self._storage_paths[configuration_type]

    def setCurrentVersions(self, current_versions: Dict[Tuple[str, int], Any]) -> None:
        """Changes the target versions to upgrade to.

        :param current_versions: A dictionary of tuples of configuration types
        and their versions currently in use, and with each of these a tuple of
        where to store this type of file and its MIME type.
        """

        self._current_versions = current_versions

    def registerCurrentVersion(self, version_info: Tuple[str, int], type_info: Any) -> None:
        if version_info in self._current_versions:
            Logger.log("d", "Overwriting current version info: %s", repr(version_info))
        self._current_versions[version_info] = type_info

    def upgrade(self) -> bool:
        """Performs the version upgrades of all configuration files to the most
        recent version.

        The upgrade plug-ins must all be loaded at this point, or no upgrades
        can be performed.

        :return: True if anything was upgraded, or False if it was already up to date.
        """
        start_time = time.time()
        Logger.log("i", "Looking for old configuration files to upgrade.")
        self._upgrade_tasks.extend(self._getUpgradeTasks())     # Get the initial files to upgrade.
        self._upgrade_routes = self._findShortestUpgradeRoutes()  # Pre-compute the upgrade routes.

        upgraded = False  # Did we upgrade something?
        while self._upgrade_tasks:
            upgrade_task = self._upgrade_tasks.popleft()
            self._upgradeFile(upgrade_task.storage_path, upgrade_task.file_name, upgrade_task.configuration_type)  # Upgrade this file.
            QCoreApplication.processEvents()  # Ensure that the GUI does not freeze.
        if upgraded:
            message = UM.Message.Message(text = catalogue.i18nc("@info:version-upgrade", "A configuration from an older version of {0} was imported.", Application.getInstance().getApplicationName()), title = catalogue.i18nc("@info:title", "Version Upgrade"))
            message.show()
        Logger.log("i", "Checking and performing updates took %s", time.time() - start_time)
        return upgraded

    def upgradeExtraFile(self, storage_path: str, file_name: str, configuration_type: str) -> None:
        """Schedules an additional file for upgrading.

        This method is intended to be called by upgrade plug-ins during
        upgrading, to make sure we also upgrade any extra files that should be
        added during the upgrade process.
        Note that the file is not immediately upgraded, but scheduled for
        upgrading. If this method is called while the ``upgrade()`` function is
        still running, it will get upgraded at the end of that run. If it is
        called while the ``upgrade()`` function is not running, it would get
        upgraded during the next call to ``upgrade()``.

        :param storage_path: The path to where the specified type of file is stored.
        :param file_name: The path to the file to upgrade, relative to the storage path.
        :param configuration_type: The file type of the specified file.
        """

        self._upgrade_tasks.append(UpgradeTask(storage_path = storage_path, file_name = file_name, configuration_type = configuration_type))

    # private:

    def _addVersionUpgrade(self, version_upgrade_plugin: PluginObject) -> None:
        """Adds a version upgrade plug-in.

        This reads from the metadata which upgrades the plug-in can perform and
        sorts the upgrade functions in memory so that the upgrades can be used
        when an upgrade is requested.

        :param version_upgrade_plugin: The plug-in object of the version upgrade plug-in.
        """

        meta_data = self._registry.getMetaData(version_upgrade_plugin.getPluginId())
        if "version_upgrade" not in meta_data:
            Logger.log("w", "Version upgrade plug-in %s doesn't define any configuration types it can upgrade.", version_upgrade_plugin.getPluginId())
            return  # Don't need to add.

        # Take a note of the source version of each configuration type. The source directories defined in each version
        # upgrade should only be limited to that version.
        src_version_dict = {}
        for item in meta_data.get("version_upgrade", {}):
            configuration_type, src_version = item
            src_version_dict[configuration_type] = src_version

        # Additional metadata about the source types: How to recognise the version and where to find them.
        if "sources" in meta_data:
            for configuration_type, source in meta_data["sources"].items():
                if "get_version" in source:
                    self._get_version_functions[configuration_type] = source["get_version"]  # May overwrite from other plug-ins that can also load the same configuration type.
                if "location" in source:
                    if configuration_type in src_version_dict:
                        src_version = src_version_dict[configuration_type]
                        if configuration_type not in self._storage_paths:
                            self._storage_paths[configuration_type] = {}
                        if src_version not in self._storage_paths[configuration_type]:
                            self._storage_paths[configuration_type][src_version] = set()
                        self._storage_paths[configuration_type][src_version] |= source["location"]

        upgrades = self._registry.getMetaData(version_upgrade_plugin.getPluginId())["version_upgrade"]
        for source, destination in upgrades.items():  # Each conversion that this plug-in can perform.
            source_type, source_version = source
            destination_type, destination_version, upgrade_function = destination

            # Fill in the dictionary representing the graph, if it doesn't have the keys yet.
            if (destination_type, destination_version) not in self._version_upgrades:
                self._version_upgrades[(destination_type, destination_version)] = set()
            self._version_upgrades[(destination_type, destination_version)].add((source_type, source_version, upgrade_function)) #Add the edge to the graph.

    def _findShortestUpgradeRoutes(self) -> Dict[Tuple[str, int], Tuple[str, int, Callable[[str, str], Optional[Tuple[List[str], List[str]]]]]]:
        """Finds the next step to take to upgrade each combination of configuration
        type and version.

        :return: A dictionary of type/version pairs that map to functions that
            upgrade said data format one step towards the most recent version, such
            that the fewest number of steps is required.
        """

        # For each (type, version) tuple, which upgrade function to use to upgrade it towards the newest versions.
        result = {}  # type: Dict[Tuple[str, int], Tuple[str, int, Callable[[str, str], Optional[Tuple[List[str], List[str]]]]]]

        # Perform a many-to-many shortest path search with Dijkstra's algorithm.
        front = collections.deque()  # type: collections.deque #Use as a queue for breadth-first iteration: Append right, pop left.
        for configuration_type, version in self._current_versions:
            front.append((configuration_type, version))
        explored_versions = set()  # type: Set[Tuple[str, int]]
        while len(front) > 0:
            destination_type, destination_version = front.popleft()  # To make it a queue, pop on the opposite side of where you append!
            if (destination_type, destination_version) in self._version_upgrades:  # We can upgrade to this version.
                for source_type, source_version, upgrade_function in self._version_upgrades[(destination_type, destination_version)]:
                    if (source_type, source_version) in explored_versions:
                        continue
                    front.append((source_type, source_version))
                    if (source_type, source_version) not in result:  # First time we encounter this version. Due to breadth-first search, this must be part of the shortest route then.
                        result[(source_type, source_version)] = (destination_type, destination_version, upgrade_function)
            explored_versions.add((destination_type, destination_version))

        return result

    def _getFilesInDirectory(self, directory: str) -> Iterator[str]:
        """Get the filenames of all files in a specified directory.

        If an exclude path is given, the specified path is ignored (relative to
        the specified directory).

        :param directory: The directory to read the files from.
        :return: The filename of each file relative to the specified directory. Note that without an * in the path, it
            will not look at sub directories.
        """

        include_sub_dirs = directory.endswith("*")
        directory_to_search = directory
        if include_sub_dirs:
            # Remove the * from the directory to search.
            directory_to_search = directory[:-1]
        for path, directory_names, file_names in os.walk(directory_to_search, topdown = True):
            if not include_sub_dirs:
                # Delete the list of sub dirs.
                directory_names.clear()
            for filename in file_names:
                relative_path = os.path.relpath(path, directory)
                yield os.path.join(relative_path, filename)

    def _getUpgradeTasks(self) -> Iterator[UpgradeTask]:
        """Gets all files that need to be upgraded.

        :return: A sequence of UpgradeTasks of files to upgrade.
        """

        storage_path_prefixes = set()
        storage_path_prefixes.add(Resources.getConfigStoragePath())
        storage_path_prefixes.add(Resources.getDataStoragePath())

        # Make sure the types and paths are ordered so we always get the same results.
        self._storage_paths = collections.OrderedDict(sorted(self._storage_paths.items()))
        for key in self._storage_paths:
            self._storage_paths[key] = collections.OrderedDict(sorted(self._storage_paths[key].items()))

        # Use pattern: /^(pattern_a|pattern_b|pattern_c|...)$/
        combined_regex_ignored_files = "^(" + "|".join(self._ignored_files) + ")"
        for old_configuration_type, version_storage_paths_dict in self._storage_paths.items():
            for src_version, storage_paths in version_storage_paths_dict.items():
                for prefix in storage_path_prefixes:
                    for storage_path in storage_paths:
                        path = os.path.join(prefix, storage_path)
                        for configuration_file in self._getFilesInDirectory(path):
                            # Get file version. Only add this upgrade task if the current file version matches with
                            # the defined version that scans through this folder.
                            if re.match(combined_regex_ignored_files, configuration_file):
                                continue
                            try:
                                with open(os.path.join(path, configuration_file), "r", encoding = "utf-8") as f:
                                    file_version = self._get_version_functions[old_configuration_type](f.read())
                                    if file_version != src_version:
                                        continue
                            except:
                                Logger.log("w", "Failed to get file version: %s, skip it", configuration_file)
                                continue

                            Logger.log("i", "Create upgrade task for configuration file [%s] with type [%s] and source version [%s]",
                                       configuration_file, old_configuration_type, file_version)
                            yield UpgradeTask(storage_path = path, file_name = configuration_file,
                                              configuration_type = old_configuration_type)

    def getFileVersion(self, configuration_type: str, file_data: str) -> Optional[int]:
        """Gets the version of the given file data"""

        if configuration_type not in self._get_version_functions:
            return None
        try:
            return self._get_version_functions[configuration_type](file_data)
        except:
            Logger.logException("w", "Unable to get version from file.")
            return None

    def _upgradeFile(self, storage_path_absolute: str, configuration_file: str, old_configuration_type: str) -> bool:
        """Upgrades a single file to any version in self._current_versions.

        A single file will be taken as source file, but may result in any number
        of output files.

        :param storage_path_absolute: The path where to find the file.
        :param configuration_file: The file to upgrade to a current version.
        :param old_configuration_type: The type of the configuration file before upgrading it.
        :return: True if the file was successfully upgraded, or False otherwise.
        """

        configuration_file_absolute = os.path.join(storage_path_absolute, configuration_file)

        # Read the old file.
        try:
            with open(configuration_file_absolute, encoding = "utf-8", errors = "ignore") as file_handle:
                files_data = [file_handle.read()]
        except MemoryError:  # File is too big. It might be the log.
            return False
        except FileNotFoundError:  # File was already moved to an /old directory.
            return False
        except IOError:
            Logger.log("w", "Can't open configuration file %s for reading.", configuration_file_absolute)
            return False

        # Get the version number of the old file.
        try:
            old_version = self._get_version_functions[old_configuration_type](files_data[0])
        except:  # Version getter gives an exception. Not a valid file. Can't upgrade it then.
            return False

        version = old_version
        configuration_type = old_configuration_type

        # Get the actual MIME type object, from the name.
        try:
            mime_type = UM.MimeTypeDatabase.MimeTypeDatabase.getMimeTypeForFile(configuration_file)
        except UM.MimeTypeDatabase.MimeTypeNotFoundError:
            return False

        filenames_without_extension = [self._stripMimeTypeExtension(mime_type, configuration_file)]
        result_data = self.updateFilesData(configuration_type, version, files_data, filenames_without_extension)
        if not result_data:
            return False
        configuration_type, version, files_data, filenames_without_extension = result_data

        # If the version changed, save the new files.
        if version != old_version or configuration_type != old_configuration_type:

            # Finding out where to store these files.
            resource_type, mime_type_name = self._current_versions[(configuration_type, version)]
            storage_path = Resources.getStoragePathForType(resource_type)
            mime_type = UM.MimeTypeDatabase.MimeTypeDatabase.getMimeType(mime_type_name)  # Get the actual MIME type object, from the name.
            if mime_type.preferredSuffix:
                extension = "." + mime_type.preferredSuffix
            elif mime_type.suffixes:
                extension = "." + mime_type.suffixes[0]
            else:
                extension = ""  # No known suffix. Put no extension behind it.
            new_filenames = [filename + extension for filename in filenames_without_extension]
            configuration_files_absolute = [os.path.join(storage_path, filename) for filename in new_filenames]

            for file_idx, configuration_file_absolute in enumerate(configuration_files_absolute):
                try:
                    with SaveFile(os.path.join(configuration_file_absolute), "w", encoding = "utf-8") as file_handle:
                        file_handle.write(files_data[file_idx])  # Save the new file.
                except IOError:
                    Logger.log("w", "Couldn't write new configuration file to %s.", configuration_file_absolute)
                    return False
            Logger.log("i", "Upgraded %s to version %s.", configuration_file, str(version))
            return True
        return False  # Version didn't change. Was already current.

    def updateFilesData(self, configuration_type: str, version: int, files_data: List[str], file_names_without_extension: List[str]) -> Optional[FilesDataUpdateResult]:
        old_configuration_type = configuration_type

        # Keep converting the file until it's at one of the current versions.
        while (configuration_type, version) not in self._current_versions:
            if (configuration_type, version) not in self._upgrade_routes:
                # No version upgrade plug-in claims to be able to upgrade this file.
                return None
            new_type, new_version, upgrade_step = self._upgrade_routes[(configuration_type, version)]
            new_file_names_without_extension = []  # type: List[str]
            new_files_data = []  # type: List[str]
            for file_idx, file_data in enumerate(files_data):
                try:
                    upgrade_step_result = upgrade_step(file_data, file_names_without_extension[file_idx])
                except Exception:  # Upgrade failed due to a coding error in the plug-in.
                    Logger.logException("w", "Exception in %s upgrade with %s: %s", old_configuration_type,
                                        upgrade_step.__module__, traceback.format_exc())
                    return None
                if upgrade_step_result:
                    this_file_names_without_extension, this_files_data = upgrade_step_result
                else:  # Upgrade failed.
                    Logger.log("w", "Unable to upgrade the file %s with %s.%s. Skipping it.",
                               file_names_without_extension[file_idx], upgrade_step.__module__, upgrade_step.__name__)
                    return None
                new_file_names_without_extension += this_file_names_without_extension
                new_files_data += this_files_data
            file_names_without_extension = new_file_names_without_extension
            files_data = new_files_data
            version = new_version
            configuration_type = new_type

        return FilesDataUpdateResult(configuration_type = configuration_type,
                                     version = version,
                                     files_data = files_data,
                                     file_names_without_extension = file_names_without_extension)

    def _stripMimeTypeExtension(self, mime_type: MimeType, file_name: str) -> str:
        suffixes = mime_type.suffixes[:]
        if mime_type.preferredSuffix:
            suffixes.append(mime_type.preferredSuffix)
        for suffix in suffixes:
            if file_name.endswith(suffix):
                return file_name[: -len(suffix) - 1]  # last -1 is for the dot separating name and extension.

        return file_name

    __instance = None   # type: VersionUpgradeManager

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "VersionUpgradeManager":
        return cls.__instance
