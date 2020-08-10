# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import datetime
import os
import os.path
import re
import shutil
import tempfile
import time  # To reduce chance of concurrency issues when deleting files if the OS is slow to register whether a file exists or not.
from typing import Dict, Generator, List, Optional, Union, cast

from UM.Logger import Logger
from UM.Platform import Platform
from UM.Version import Version


class ResourceTypeError(Exception):
    pass


class UnsupportedStorageTypeError(Exception):
    pass


class Resources:
    """Class to look up any form of resource used by Uranium or an application using Uranium"""

    Resources = 1
    """The main resources location. Equal to $resource_search_path/resources."""
    Preferences = 2
    """Location of preference configuration files. Actual location depends on platform."""
    Meshes = 3
    """Location of meshes. Equal to $resources/meshes."""
    Shaders = 4
    """Location of shaders. Equal to $resources/shaders."""
    i18n = 5
    """Location of translation files. Equal to $resources/i18n."""
    Images = 6
    """Location of images not in the theme. Equal to $resources/images."""
    Themes = 7
    """Location of themes. Equal to $resources/themes."""
    DefinitionContainers = 8
    """Location of definition container files. Equal to $resources/definitions"""
    InstanceContainers = 9
    """Location of instance container files. Equal to $resources/instances"""
    ContainerStacks = 10
    """Location of container stack files. Equal to $resources/stacks"""
    Cache = 11
    """Location of cached data"""
    Plugins = 12
    """Location of plugins"""
    BundledPackages = 13
    """Location of data regarding bundled packages"""
    Texts = 14
    """Location of text files"""

    UserType = 128
    """Any custom resource types should be greater than this to prevent collisions with standard types."""

    ApplicationIdentifier = "UM"
    ApplicationVersion = "unknown"

    __bundled_resources_path = None #type: Optional[str]

    @classmethod
    def getPath(cls, resource_type: int, *args) -> str:
        """Get the path to a certain resource file

        :param resource_type: :type{int} The type of resource to retrieve a path for.
        :param args: Arguments that are appended to the location to locate the correct file.

        :return: An absolute path to a file.
            If a file exists in any storage path, it is returned without searching other paths.
            If multiple files are found the first found is returned.

        :exception FileNotFoundError: Raised when the file could not be found.
        """

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

    @classmethod
    def getAllResourcesOfType(cls, resource_type: int) -> List[str]:
        """Get a list of paths to all resources of a certain resource type.

        :param resource_type: The resource type to get the paths for.

        :return: A list of absolute paths to resources of the specified type.
        """

        files = {} #type: Dict[str, List[str]]
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
                        if entry not in files:
                            files[entry] = []
                        files[entry].append(os.path.join(root, entry))

        result = []
        for name, paths in files.items():
            result.append(paths[0])

        return result

    @classmethod
    def getStoragePath(cls, resource_type: int, *args) -> str:
        """Get the path that can be used to write a certain resource file.

        :param resource_type: The type of resource to retrieve a path for.
        :param args: Arguments that are appended to the location for the correct path.

        :return: A path that can be used to write the file.

        :note This method does not check whether a given file exists.
        """

        return os.path.join(cls.getStoragePathForType(resource_type), *args)

    @classmethod
    def getAllPathsForType(cls, resource_type: int) -> List[str]:
        """Return a list of paths for a certain resource type.

        :param resource_type: The type of resource to retrieve.
        :return: A list of absolute paths where the resource type can be found.

        :exception TypeError Raised when type is an unknown value.
        """

        if resource_type not in cls.__types:
            raise ResourceTypeError("Unknown type {0}".format(resource_type))

        paths = set()

        try:
            paths.add(cls.getStoragePathForType(resource_type))
        except UnsupportedStorageTypeError:
            pass

        for path in cls.__paths:
            paths.add(os.path.join(path, cls.__types[resource_type]))

        return list(paths)

    @classmethod
    def getStoragePathForType(cls, resource_type: int) -> str:
        """Return a path where a certain resource type can be stored.

        :param type: The type of resource to store.
        :return: An absolute path where the given resource type can be stored.

        :exception UnsupportedStorageTypeError Raised when writing type is not supported.
        """

        if resource_type not in cls.__types_storage:
            raise UnsupportedStorageTypeError("Unknown storage type {0}".format(resource_type))

        if cls.__config_storage_path is None or cls.__data_storage_path is None:
            cls.__initializeStoragePaths()

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

    @classmethod
    def addSearchPath(cls, path: str) -> None:
        """Add a path relative to which resources should be searched for.

        :param path: The path to add.
        """

        if os.path.isdir(path) and path not in cls.__paths:
            cls.__paths.append(path)

    @classmethod
    def removeSearchPath(cls, path: str) -> None:
        """Remove a resource search path."""

        if path in cls.__paths:
            del cls.__paths[cls.__paths.index(path)]

    @classmethod
    def addType(cls, resource_type: int, path: str) -> None:
        """Add a custom resource type that can be located.

        :param resource_type: An integer that can be used to identify the type. Should be greater than UserType.
        :param path: The path relative to the search paths where resources of this type can be found./
        """

        if resource_type in cls.__types:
            raise ResourceTypeError("Type {0} already exists".format(resource_type))

        if resource_type <= cls.UserType:
            raise ResourceTypeError("Type should be greater than Resources.UserType")

        cls.__types[resource_type] = path

    @classmethod
    def addStorageType(cls, resource_type: int, path: str) -> None:
        """Add a custom storage path for a resource type.

        :param resource_type: The type to add a storage path for.
        :param path: The path to add as storage path. Should be relative to the resources storage path.
        """

        if resource_type in cls.__types:
            raise ResourceTypeError("Type {0} already exists".format(resource_type))

        cls.__types[resource_type] = path
        cls.__types_storage[resource_type] = path

    @classmethod
    def getConfigStoragePath(cls) -> str:
        """Gets the configuration storage path.

        This is where the application stores user configuration, such as
        preferences.
        """

        if not cls.__config_storage_path:
            cls.__initializeStoragePaths()
        return cls.__config_storage_path

    @classmethod
    def getDataStoragePath(cls) -> str:
        """Gets the data storage path.

        This is where the application stores user files, such as profiles.
        """

        if not cls.__data_storage_path:
            cls.__initializeStoragePaths()
        return cls.__data_storage_path

    @classmethod
    def getCacheStoragePath(cls) -> str:
        """Gets the cache storage path.

        This is where the application stores cache files.
        """

        if not cls.__cache_storage_path:
            cls.__initializeStoragePaths()
        return cls.__cache_storage_path

    @classmethod
    def getSearchPaths(cls) -> Generator[str, None, None]:
        """Gets the search paths for resources.

        :return: A sequence of paths where resources might be.
        """

        yield from cls.__paths

    @classmethod
    def removeType(cls, resource_type: int) -> None:
        """Remove a custom resource type."""

        if resource_type not in cls.__types:
            return

        if resource_type <= cls.UserType:
            raise ResourceTypeError("Uranium standard types cannot be removed")

        del cls.__types[resource_type]

        if resource_type in cls.__types_storage:
            del cls.__types_storage[resource_type]

    @classmethod
    def factoryReset(cls) -> None:
        """Performs a factory reset, compressing the current state of configuration
        into an archive and emptying the resource folders.

        When calling this function, be sure to quit the application immediately
        afterwards, lest the save function write the configuration anew.
        """

        config_path = cls.getConfigStoragePath()
        data_path = cls.getDataStoragePath()
        cache_path = cls.getCacheStoragePath()

        folders_to_backup = set()
        folders_to_remove = set()  # only cache folder needs to be removed

        folders_to_backup.add(config_path)
        folders_to_backup.add(data_path)

        # Only remove the cache folder if it's not the same as data or config
        if cache_path not in folders_to_backup:
            folders_to_remove.add(cache_path)

        for folder in folders_to_remove:
            shutil.rmtree(folder, ignore_errors = True)
        for folder in folders_to_backup:
            base_name = os.path.basename(folder)
            root_dir = os.path.dirname(folder)

            date_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            idx = 0
            file_name = base_name + "_" + date_now
            zip_file_path = os.path.join(root_dir, file_name + ".zip")
            while os.path.exists(zip_file_path):
                idx += 1
                file_name = base_name + "_" + date_now + "_" + str(idx)
                zip_file_path = os.path.join(root_dir, file_name + ".zip")
            try:
                # only create the zip backup when the folder exists
                if os.path.exists(folder):
                    # remove the .zip extension because make_archive() adds it
                    zip_file_path = zip_file_path[:-4]
                    shutil.make_archive(zip_file_path, "zip", root_dir = root_dir, base_dir = base_name)

                    # remove the folder only when the backup is successful
                    shutil.rmtree(folder, ignore_errors = True)

                # create an empty folder so Resources will not try to copy the old ones
                os.makedirs(folder, 0o0755, exist_ok=True)

            except:
                Logger.logException("e", "Failed to backup [%s] to file [%s]", folder, zip_file_path)

    @classmethod
    def __find(cls, resource_type: int, *args: str) -> List[str]:
        """Returns a list of paths where args was found."""

        suffix = cls.__types.get(resource_type, None)
        if suffix is None:
            return []

        files = []
        for path in cls.__paths:
            file_path = os.path.join(path, suffix, *args)
            if os.path.exists(file_path):
                files.append(file_path)
        return files

    @classmethod
    def _getConfigStorageRootPath(cls) -> str:
        # Returns the path where we store different versions of app configurations
        if Platform.isWindows():
            config_path = os.getenv("APPDATA")
            if not config_path: # Protect if the getenv function returns None (it should never happen)
                config_path = "."
        elif Platform.isOSX():
            config_path = os.path.expanduser("~/Library/Application Support")
        elif Platform.isLinux():
            try:
                config_path = os.environ["XDG_CONFIG_HOME"]
            except KeyError:
                config_path = os.path.expanduser("~/.config")
        else:
            config_path = "."

        return config_path

    @classmethod
    def _getPossibleConfigStorageRootPathList(cls) -> List[str]:
        # Returns all possible root paths for storing app configurations (in old and new versions)
        config_root_list = [Resources._getConfigStorageRootPath()]
        if Platform.isWindows():
            # it used to be in LOCALAPPDATA on Windows
            config_path = os.getenv("LOCALAPPDATA")
            if config_path: # Protect if the getenv function returns None (it should never happen)
                config_root_list.append(config_path)
        elif Platform.isOSX():
            config_root_list.append(os.path.expanduser("~"))

        config_root_list = [os.path.join(n, cls.ApplicationIdentifier) for n in config_root_list]
        return config_root_list

    @classmethod
    def _getPossibleDataStorageRootPathList(cls) -> List[str]:
        data_root_list = []

        # Returns all possible root paths for storing app configurations (in old and new versions)
        if Platform.isLinux():
            # We can cast here to str since the _getDataStorageRootPath always returns a string if platform is Linux
            data_root_list.append(os.path.join(cast(str, Resources._getDataStorageRootPath()), cls.ApplicationIdentifier))
        else:
            # on Windows and Mac, data and config are saved in the same place
            data_root_list = Resources._getPossibleConfigStorageRootPathList()

        return data_root_list

    @classmethod
    def _getDataStorageRootPath(cls) -> Optional[str]:
        # Returns the path where we store different versions of app data
        data_path = None
        if Platform.isLinux():
            try:
                data_path = os.environ["XDG_DATA_HOME"]
            except KeyError:
                data_path = os.path.expanduser("~/.local/share")
        return data_path

    @classmethod
    def _getCacheStorageRootPath(cls) -> Optional[str]:
        # Returns the path where we store different versions of app configurations
        cache_path = None
        if Platform.isWindows():
            cache_path = os.getenv("LOCALAPPDATA")
        elif Platform.isOSX():
            cache_path = None
        elif Platform.isLinux():
            try:
                cache_path = os.environ["XDG_CACHE_HOME"]
            except KeyError:
                cache_path = os.path.expanduser("~/.cache")

        return cache_path

    @classmethod
    def __initializeStoragePaths(cls) -> None:
        Logger.log("d", "Initializing storage paths")
        # use nested structure: <app-name>/<version>/...
        if cls.ApplicationVersion == "master" or cls.ApplicationVersion == "unknown":
            storage_dir_name = os.path.join(cls.ApplicationIdentifier, cls.ApplicationVersion)
        else:
            version = Version(cls.ApplicationVersion)
            storage_dir_name = os.path.join(cls.ApplicationIdentifier, "%s.%s" % (version.getMajor(), version.getMinor()))

        # config is saved in "<CONFIG_ROOT>/<storage_dir_name>"
        cls.__config_storage_path = os.path.join(Resources._getConfigStorageRootPath(), storage_dir_name)
        Logger.log("d", "Config storage path is %s", cls.__config_storage_path)

        # data is saved in
        #  - on Linux: "<DATA_ROOT>/<storage_dir_name>"
        #  - on other: "<CONFIG_DIR>" (in the config directory)
        data_root_path = Resources._getDataStorageRootPath()
        cls.__data_storage_path = cls.__config_storage_path if data_root_path is None else \
            os.path.join(data_root_path, storage_dir_name)
        Logger.log("d", "Data storage path is %s", cls.__data_storage_path)
        # cache is saved in
        #  - on Linux:   "<CACHE_DIR>/<storage_dir_name>"
        #  - on Windows: "<CACHE_DIR>/<storage_dir_name>/cache"
        #  - on Mac:     "<CONFIG_DIR>/cache" (in the config directory)
        cache_root_path = Resources._getCacheStorageRootPath()
        if cache_root_path is None:
            cls.__cache_storage_path = os.path.join(cls.__config_storage_path, "cache")
        else:
            cls.__cache_storage_path = os.path.join(cache_root_path, storage_dir_name)
            if Platform.isWindows():
                cls.__cache_storage_path = os.path.join(cls.__cache_storage_path, "cache")
        Logger.log("d", "Cache storage path is %s", cls.__cache_storage_path)
        if not os.path.exists(cls.__config_storage_path) or not os.path.exists(cls.__data_storage_path):
            cls._copyLatestDirsIfPresent()

        cls.__paths.insert(0, cls.__data_storage_path)

    @classmethod
    def _copyLatestDirsIfPresent(cls) -> None:
        """Copies the directories of the latest version on this machine if present, so the upgrade will use the copies
        as the base for upgrade. See CURA-3529 for more details.
        """

        # Paths for the version we are running right now
        this_version_config_path = Resources.getConfigStoragePath()
        this_version_data_path = Resources.getDataStoragePath()

        # Find the latest existing directories on this machine
        config_root_path_list = Resources._getPossibleConfigStorageRootPathList()
        data_root_path_list = Resources._getPossibleDataStorageRootPathList()

        Logger.log("d", "Found config: %s and data: %s", config_root_path_list, data_root_path_list)

        latest_config_path = Resources._findLatestDirInPaths(config_root_path_list, dir_type = "config")
        latest_data_path = Resources._findLatestDirInPaths(data_root_path_list, dir_type = "data")
        Logger.log("d", "Latest config path: %s and latest data path: %s", latest_config_path, latest_data_path)
        if not latest_config_path:
            # No earlier storage dirs found, do nothing
            return

        # Copy config folder if needed
        if latest_config_path == this_version_config_path:
            # If the directory found matches the current version, do nothing
            Logger.log("d", "Same config path [%s], do nothing.", latest_config_path)
        else:
            cls.copyVersionFolder(latest_config_path, this_version_config_path)

        # Copy data folder if needed
        if latest_data_path == this_version_data_path:
            # If the directory found matches the current version, do nothing
            Logger.log("d", "Same data path [%s], do nothing.", latest_config_path)
        else:
            # If the data dir is the same as the config dir, don't copy again
            if latest_data_path is not None and os.path.exists(latest_data_path) and latest_data_path != latest_config_path:
                cls.copyVersionFolder(latest_data_path, this_version_data_path)

        # Remove "cache" if we copied it together with config
        suspected_cache_path = os.path.join(this_version_config_path, "cache")
        if os.path.exists(suspected_cache_path):
            try:
                shutil.rmtree(suspected_cache_path)
            except EnvironmentError:  # No rights to this directory or it gets deleted asynchronously.
                try:
                    time.sleep(1)
                    shutil.rmtree(suspected_cache_path)  # Sometimes it seems to help to try again after a short while, to prevent concurrency issues.
                except EnvironmentError:
                    Logger.error("Failed to delete cache, cache might be outdated and lead to weird errors: {err}")
                    pass

    @classmethod
    def copyVersionFolder(cls, src_path: str, dest_path: str) -> None:
        Logger.log("i", "Copying directory from '%s' to '%s'", src_path, dest_path)
        # we first copy everything to a temporary folder, and then move it to the new folder
        base_dir_name = os.path.basename(src_path)
        temp_root_dir_path = tempfile.mkdtemp("cura-copy")
        temp_dir_path = os.path.join(temp_root_dir_path, base_dir_name)
        # src -> temp -> dest
        try:
            # Copy everything, except for the logs, lock or really old (we used to copy old configs to the "old" folder)
            # config files.
            shutil.copytree(src_path, temp_dir_path,
                            ignore = shutil.ignore_patterns("*.lock", "*.log", "*.log.?", "old"))
            # if the dest_path exist, it needs to be removed first
            if not os.path.exists(dest_path):
                shutil.move(temp_dir_path, dest_path)
            else:
                Logger.log("e", "Unable to copy files to %s as the folder already exists", dest_path)
        except:
            Logger.log("e", "Something occurred when copying the version folder from '%s' to '%s'", src_path, dest_path)

    @classmethod
    def _findLatestDirInPaths(cls, search_path_list: List[str], dir_type: str = "config") -> Optional[str]:
        # version dir name must match: <digit(s)>.<digit(s)>
        version_regex = re.compile(r"^[0-9]+\.[0-9]+$")
        check_dir_type_func_dict = {
            "data": Resources._isNonVersionedDataDir,
            "config": Resources._isNonVersionedConfigDir
        }
        check_dir_type_func = check_dir_type_func_dict[dir_type]

        # CURA-6744
        # If the application version matches "<major>.<minor>", create a Version object for it for comparison, so we
        # can find the directory with the highest version that's below the application version.
        # An application version that doesn't match "<major>.<minor>", e.g. "master", probably indicates a temporary
        # version, and in this case, this temporary version is treated as the latest version. It will ONLY upgrade from
        # a highest "<major>.<minor>" version if it's present.
        # For app version, there can be extra version strings at the end. For comparison, we only want the
        # "<major>.<minor>.<patch>" part. Here we use a regex to find that part in the app version string.
        semantic_version_regex = re.compile(r"(^[0-9]+\.([0-9]+)*).*$")
        app_version = None  # type: Optional[Version]
        app_version_str = cls.ApplicationVersion
        if app_version_str is not None:
            result = semantic_version_regex.match(app_version_str)
            if result is not None:
                app_version_str = result.group(0)
                app_version = Version(app_version_str)

        latest_config_path = None  # type: Optional[str]
        for search_path in search_path_list:
            if not os.path.exists(search_path):
                continue

            # Give priority to a folder with files with version number in it
            try:
                storage_dir_name_list = next(os.walk(search_path))[1]
            except StopIteration:  # There is no next().
                continue

            match_dir_name_list = [n for n in storage_dir_name_list if version_regex.match(n) is not None]
            match_dir_version_list = [{"dir_name": n, "version": Version(n)} for n in match_dir_name_list]  # type: List[Dict[str, Union[str, Version]]]
            match_dir_version_list = sorted(match_dir_version_list, key = lambda x: x["version"], reverse = True)
            if app_version is not None:
                match_dir_version_list = list(x for x in match_dir_version_list if x["version"] < app_version)

            if len(match_dir_version_list) > 0:
                if isinstance(match_dir_version_list[0]["dir_name"], str):
                    latest_config_path = os.path.join(search_path, match_dir_version_list[0]["dir_name"])  # type: ignore

            if latest_config_path is not None:
                break

            # If not, check if there is a non versioned data dir
            if check_dir_type_func(search_path):
                latest_config_path = search_path
                break

        return latest_config_path

    @classmethod
    def _isNonVersionedDataDir(cls, check_path: str) -> bool:
        dirs, files = next(os.walk(check_path))[1:]
        valid_dir_names = [dn for dn in dirs if dn in Resources.__expected_dir_names_in_data]

        return len(valid_dir_names) > 0

    @classmethod
    def _isNonVersionedConfigDir(cls, check_path: str) -> bool:
        dirs, files = next(os.walk(check_path))[1:]
        valid_file_names = [fn for fn in files if fn.endswith(".cfg")]

        return len(valid_file_names) > 0

    @classmethod
    def addExpectedDirNameInData(cls, dir_name: str) -> None:
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
        Plugins: "plugins",
        BundledPackages: "bundled_packages",
        Texts: "texts",
    } #type: Dict[int, str]
    __types_storage = {
        Resources: "",
        Preferences: "",
        Cache: "",
        DefinitionContainers: "definitions",
        InstanceContainers: "instances",
        ContainerStacks: "stacks",
        Themes: "themes",
        Plugins: "plugins",
    } #type: Dict[int, str]
