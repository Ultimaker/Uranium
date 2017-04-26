# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import os.path
import re
import shutil
from typing import List

from PyQt5.QtCore import QStandardPaths

from UM.Logger import Logger
from UM.Platform import Platform

class ResourceTypeError(Exception):
    pass


class UnsupportedStorageTypeError(Exception):
    pass


##  Class to look up any form of resource used by Uranium or an application using Uranium
class Resources:
    ## The main resources location. Equal to $resource_search_path/resources.
    Resources = 1
    ## Location of preference configuration files. Actual location depends on platform.
    Preferences = 2
    ## Location of meshes. Equal to $resources/meshes.
    Meshes = 3
    ## Location of shaders. Equal to $resources/shaders.
    Shaders = 4
    ## Location of translation files. Equal to $resources/i18n.
    i18n = 5
    ## Location of images not in the theme. Equal to $resources/images.
    Images = 6
    ## Location of themes. Equal to $resources/themes.
    Themes = 7
    ## Location of definition container files. Equal to $resources/definitions
    DefinitionContainers = 8
    ## Location of instance container files. Equal to $resources/instances
    InstanceContainers = 9
    ## Location of container stack files. Equal to $resources/stacks
    ContainerStacks = 10
    ## Location of cached data
    Cache = 11

    ## Any custom resource types should be greater than this to prevent collisions with standard types.
    UserType = 128

    ApplicationIdentifier = "UM"
    ApplicationVersion = "unknown"

    ##  Get the path to a certain resource file
    #
    #   \param resource_type \type{int} The type of resource to retrieve a path for.
    #   \param args Arguments that are appended to the location to locate the correct file.
    #
    #   \return An absolute path to a file.
    #           If a file exists in any storage path, it is returned without searching other paths.
    #           If multiple files are found the first found is returned.
    #
    #   \exception FileNotFoundError Raised when the file could not be found.
    @classmethod
    def getPath(cls, resource_type: int, *args) -> str:
        try:
            path = cls.getStoragePath(resource_type, *args)
            if os.path.exists(path):
                return path
        except UnsupportedStorageTypeError:
            pass

        paths = cls.__find(resource_type, *args)
        if paths:
            return paths[0]

        raise FileNotFoundError("Could not find resource {0} in {1}".format(args, resource_type))

    ##  Get a list of paths to all resources of a certain resource type.
    #
    #   \param resource_type The resource type to get the paths for.
    #
    #   \return A list of absolute paths to resources of the specified type.
    @classmethod
    def getAllResourcesOfType(cls, resource_type: int) -> List[str]:
        files = {}
        search_dirs = cls.getAllPathsForType(resource_type)

        for directory in search_dirs:
            if not os.path.isdir(directory):
                continue

            for root, dirnames, entries in os.walk(directory, followlinks = True):
                dirname = root.replace(directory, "")
                if os.sep + "." in dirname:
                    continue
                for entry in entries:
                    if not entry.startswith('.') and os.path.isfile(os.path.join(root, entry)):
                        if not entry in files:
                            files[entry] = []
                        files[entry].append(os.path.join(root, entry))

        result = []
        for name, paths in files.items():
            result.append(paths[0])

        return result

    ##  Get the path that can be used to write a certain resource file.
    #
    #   \param resource_type The type of resource to retrieve a path for.
    #   \param args Arguments that are appended to the location for the correct path.
    #
    #   \return A path that can be used to write the file.
    #
    #   \note This method does not check whether a given file exists.
    @classmethod
    def getStoragePath(cls, resource_type: int, *args) -> str:
        return os.path.join(cls.getStoragePathForType(resource_type), *args)

    ##  Return a list of paths for a certain resource type.
    #
    #   \param resource_type \type{int} The type of resource to retrieve.
    #   \return \type{list} A list of absolute paths where the resource type can be found.
    #
    #   \exception TypeError Raised when type is an unknown value.
    @classmethod
    def getAllPathsForType(cls, resource_type: int) -> List[str]:
        if resource_type not in cls.__types:
            raise ResourceTypeError("Unknown type {0}".format(resource_type))

        paths = []

        try:
            paths.append(cls.getStoragePathForType(resource_type))
        except UnsupportedStorageTypeError:
            pass

        for path in cls.__paths:
            paths.append(os.path.join(path, cls.__types[resource_type]))

        return paths

    ##  Return a path where a certain resource type can be stored.
    #
    #   \param type \type{int} The type of resource to store.
    #   \return \type{string} An absolute path where the given resource type can be stored.
    #
    #   \exception UnsupportedStorageTypeError Raised when writing type is not supported.
    @classmethod
    def getStoragePathForType(cls, resource_type: int) -> str:
        if resource_type not in cls.__types_storage:
            raise UnsupportedStorageTypeError("Unknown storage type {0}".format(resource_type))

        if cls.__config_storage_path is None or cls.__data_storage_path is None:
            cls.__initializeStoragePaths()

        path = None
        # Special casing for Linux, since configuration should be stored in ~/.config but data should be stored in ~/.local/share
        if resource_type == cls.Preferences:
            path = cls.__config_storage_path
        elif resource_type == cls.Cache:
            path = cls.__cache_storage_path
        else:
            path = os.path.join(cls.__data_storage_path, cls.__types_storage[resource_type])

        # Ensure the directory we want to write to exists
        try:
            os.makedirs(path)
        except OSError:
            pass

        return path

    ##  Add a path relative to which resources should be searched for.
    #
    #   \param path The path to add.
    @classmethod
    def addSearchPath(cls, path: str):
        if os.path.isdir(path) and path not in cls.__paths:
            cls.__paths.append(path)

    ##  Remove a resource search path.
    @classmethod
    def removeSearchPath(cls, path: str):
        if path in cls.__paths:
            del cls.__paths[cls.__paths.index(path)]

    ##  Add a custom resource type that can be located.
    #
    #   \param type \type{int} An integer that can be used to identify the type. Should be greater than UserType.
    #   \param path \type{string} The path relative to the search paths where resources of this type can be found./
    @classmethod
    def addType(cls, resource_type: int, path: str):
        if resource_type in cls.__types:
            raise ResourceTypeError("Type {0} already exists".format(resource_type))

        if resource_type <= cls.UserType:
            raise ResourceTypeError("Type should be greater than Resources.UserType")

        cls.__types[resource_type] = path

    ##  Add a custom storage path for a resource type.
    #
    #   \param type The type to add a storage path for.
    #   \param path The path to add as storage path. Should be relative to the resources storage path.
    @classmethod
    def addStorageType(cls, resource_type: int, path: str):
        if resource_type in cls.__types:
            raise ResourceTypeError("Type {0} already exists".format(resource_type))

        cls.__types[resource_type] = path
        cls.__types_storage[resource_type] = path

    ##  Gets the configuration storage path.
    #
    #   This is where the application stores user configuration, such as
    #   preferences.
    @classmethod
    def getConfigStoragePath(cls) -> str:
        if not cls.__config_storage_path:
            cls.__initializeStoragePaths()
        return cls.__config_storage_path

    ##  Gets the data storage path.
    #
    #   This is where the application stores user files, such as profiles.
    @classmethod
    def getDataStoragePath(cls) -> str:
        if not cls.__data_storage_path:
            cls.__initializeStoragePaths()
        return cls.__data_storage_path

    ##  Gets the search paths for resources.
    #
    #   \return A sequence of paths where resources might be.
    @classmethod
    def getSearchPaths(cls):
        yield from cls.__paths

    ##  Remove a custom resource type.
    @classmethod
    def removeType(cls, resource_type: int):
        if resource_type not in cls.__types:
            return

        if resource_type <= cls.UserType:
            raise ResourceTypeError("Uranium standard types cannot be removed")

        del cls.__types[resource_type]

        if resource_type in cls.__types_storage:
            del cls.__types_storage[resource_type]

    ## private:

    # Returns a list of paths where args was found.
    @classmethod
    def __find(cls, resource_type: int, *args) -> List[str]:
        suffix = cls.__types.get(resource_type, None)
        if suffix is None:
            return None

        files = []
        for path in cls.__paths:
            file_path = os.path.join(path, suffix, *args)
            if os.path.exists(file_path):
                files.append(file_path)
        return files

    # Returns all possible root paths for storing app configurations (in old and new versions)
    @classmethod
    def _getPossibleConfigStorageRootPathList(cls):
        config_root_list = [Resources._getConfigStorageRootPath()]

        if Platform.isOSX():
            # Config storage path on OSX used to be ~/.cura but changed to ~/Library/Application Support/Cura for 2.3 and later.
            config_root_list.append(os.path.join(os.path.expanduser("~"), cls.ApplicationIdentifier))
            # Config storage path on OSX used to be ~/Library/Application Support/cura but changed to ~/Library/Preferences/cura for 2.6.
            config_root_list.append(os.path.normpath(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)))

        return config_root_list

    # Returns all possible root paths for storing app data (in old and new versions)
    @classmethod
    def _getPossibleDataStorageRootPathList(cls) -> List[str]:
        data_root_list = [Resources._getDataStorageRootPath()]

        if Platform.isWindows():
            # Data storage path on Windows is now ~/AppData/Roaming/cura but used to be ~/AppData/Local/cura (changed since 2.6)
            data_root_list.append(os.path.normpath(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)))
        elif Platform.isOSX():
            # Data storage path on OSX used to be ~/.cura but is now ~/Library/Application Support/Cura (changed since 2.3)
            data_root_list.append(os.path.join(os.path.expanduser("~"), cls.ApplicationIdentifier))

        return data_root_list

    # Returns the path where we store different versions of app configurations
    @classmethod
    def _getConfigStorageRootPath(cls):
        # Equals ~/.config/<appname> on Linux, ~/Library/Preferences/<appname> on OSX, ~/AppData/Local/<appname> on Windows.
        return os.path.normpath(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation))

    # Returns the path where we store different versions of app data
    @classmethod
    def _getDataStorageRootPath(cls):
        # Equals ~/.local/share/<appname> on Linux, ~/Library/Application Support/<appname> on OSX, ~/AppData/Roaming/<appname> on Windows.
        return os.path.normpath(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))

    # Returns the path where we store different versions of app configurations
    @classmethod
    def _getCacheStorageRootPath(cls):
        # Equals ~/.cache/<appname> on Linux, ~/Library/Caches/<appname> on OSX, ~/AppData/Local/<appname>/cache on Windows.
        return os.path.normpath(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))

    @classmethod
    def __initializeStoragePaths(cls):
        Logger.log("d", "Initializing storage paths")
        # use nested structure: <app-name>/<version>/...
        if cls.ApplicationVersion == "master" or cls.ApplicationVersion == "unknown":
            storage_dir_name = cls.ApplicationVersion
        else:
            from UM.Version import Version
            version = Version(cls.ApplicationVersion)
            storage_dir_name = "%s.%s" % (version.getMajor(), version.getMinor())

        cls.__config_storage_path = os.path.join(Resources._getConfigStorageRootPath(), storage_dir_name)
        Logger.log("d", "Config storage path is %s", cls.__config_storage_path)

        cls.__data_storage_path = os.path.join(Resources._getDataStorageRootPath(), storage_dir_name)
        Logger.log("d", "Data storage path is %s", cls.__data_storage_path)

        cls.__cache_storage_path = os.path.join(Resources._getCacheStorageRootPath(), storage_dir_name)
        Logger.log("d", "Cache storage path is %s", cls.__cache_storage_path)

        if not os.path.exists(cls.__config_storage_path):
            cls._copyLatestDirsIfPresent()

        cls.__paths.insert(0, cls.__data_storage_path)

    ##  Copies the directories of the latest version on this machine if present, so the upgrade will use the copies
    #   as the base for upgrade. See CURA-3529 for more details.
    @classmethod
    def _copyLatestDirsIfPresent(cls):
        # Paths for the version we are running right now
        this_version_config_path = Resources.getConfigStoragePath()
        this_version_data_path = Resources.getDataStoragePath()

        # Find the latest existing directories on this machine
        config_root_path_list = Resources._getPossibleConfigStorageRootPathList()
        data_root_path_list = Resources._getPossibleDataStorageRootPathList()

        Logger.log("d", "Found config: %s and data: %s", config_root_path_list, data_root_path_list)

        latest_config_path = Resources._findLatestDirInPaths(config_root_path_list, dir_type="config")
        latest_data_path = Resources._findLatestDirInPaths(data_root_path_list, dir_type="data")
        Logger.log("d", "Latest config path: %s and latest data path: %s", latest_config_path, latest_data_path)
        if not latest_config_path:
            # No earlier storage dirs found, do nothing
            return

        if latest_config_path == this_version_config_path:
            # If the directory found matches the current version, do nothing
            return

        # Prevent circular import
        import UM.VersionUpgradeManager
        UM.VersionUpgradeManager.VersionUpgradeManager.getInstance().copyVersionFolder(latest_config_path, this_version_config_path)
        # If the data dir is the same as the config dir, don't copy again
        if latest_data_path is not None and os.path.exists(latest_data_path) and latest_data_path != latest_config_path:
            UM.VersionUpgradeManager.VersionUpgradeManager.getInstance().copyVersionFolder(latest_data_path, this_version_data_path)

        # Remove "cache" if we copied it together with config
        suspected_cache_path = os.path.join(this_version_config_path, "cache")
        if os.path.exists(suspected_cache_path):
            shutil.rmtree(suspected_cache_path)

    @classmethod
    def _findLatestDirInPaths(cls, search_path_list, dir_type="config"):
        # version dir name must match: <digit(s)>.<digit(s)><whatever>
        version_regex = re.compile(r'^[0-9]+\.[0-9]+.*$')
        check_dir_type_func_dict = {"config": Resources._isNonVersionedConfigDir,
                                    "data": Resources._isNonVersionedDataDir,
                                    }
        check_dir_type_func = check_dir_type_func_dict[dir_type]

        latest_config_path = None
        for search_path in search_path_list:
            if not os.path.exists(search_path):
                continue

            if check_dir_type_func(cls, search_path):
                latest_config_path = search_path
                break

            storage_dir_name_list = next(os.walk(search_path))[1]
            if storage_dir_name_list:
                storage_dir_name_list = sorted(storage_dir_name_list, reverse=True)
                # for now we use alphabetically ordering to determine the latest version (excluding master)
                for dir_name in storage_dir_name_list:
                    if dir_name.endswith("master"):
                        continue
                    if version_regex.match(dir_name) is None:
                        continue

                    # make sure that the version we found is not newer than the current version
                    if version_regex.match(cls.ApplicationVersion):
                        later_version = sorted([cls.ApplicationVersion, dir_name], reverse=True)[0]
                        if cls.ApplicationVersion != later_version:
                            continue

                    latest_config_path = os.path.join(search_path, dir_name)
                    break
            if latest_config_path is not None:
                break
        return latest_config_path

    def _isNonVersionedDataDir(cls, check_path):
        # checks if the given path is (probably) a valid app directory for a version earlier than 2.6
        if not cls.__expected_dir_names_in_data:
            return True

        dirs, files = next(os.walk(check_path))[1:]
        valid_dir_names = [dn for dn in dirs if dn in Resources.__expected_dir_names_in_data]
        return valid_dir_names

    def _isNonVersionedConfigDir(cls, check_path):
        dirs, files = next(os.walk(check_path))[1:]
        valid_file_names = [fn for fn in files if fn.endswith(".cfg")]

        return bool(valid_file_names)

    @classmethod
    def addExpectedDirNameInData(cls, dir_name):
        cls.__expected_dir_names_in_data.append(dir_name)

    __expected_dir_names_in_data = []  # type: List[str]

    __config_storage_path = None    # type: str
    __data_storage_path = None      # type: str
    __cache_storage_path = None     # type: str

    __paths = []    # type: List[str]
    __types = {
        Resources: "",
        Preferences: "",
        Cache: "",
        Meshes: "meshes",
        Shaders: "shaders",
        i18n: "i18n",
        Images: "images",
        Themes: "themes",
        DefinitionContainers: "definitions",
        InstanceContainers: "instances",
        ContainerStacks: "stacks",
    }
    __types_storage = {
        Resources: "",
        Preferences: "",
        Cache: "",
        InstanceContainers: "instances",
        ContainerStacks: "stacks",
    }
