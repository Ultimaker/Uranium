# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import os.path
import platform
import sys

class TypeError(Exception):
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
    ## Location of machine definition files. Equal to $resources/machines
    MachineDefinitions = 8
    ## Location of machine instance files. Equal to $resources/machine_instances
    MachineInstances = 9
    ## Location of setting profile files. Equal to $resources/profiles
    Profiles = 10
    ## Location of working profiles for each machine instance. Equal to $resources/instance_profiles
    MachineInstanceProfiles = 11

    ## Any custom resource types should be greater than this to prevent collisions with standard types.
    UserType = 128

    ApplicationIdentifier = "UM"

    ##  Get the path to a certain resource file
    #
    #   \param type \type{int} The type of resource to retrieve a path for.
    #   \param args Arguments that are appended to the location to locate the correct file.
    #
    #   \return An absolute path to a file.
    #           If a file exists in any storage path, it is returned without searching other paths.
    #           If multiple files are found the first found is returned.
    #
    #   \exception FileNotFoundError Raised when the file could not be found.
    @classmethod
    def getPath(cls, type, *args):
        try:
            path = cls.getStoragePath(type, *args)
            if os.path.exists(path):
                return path
        except UnsupportedStorageTypeError:
            pass

        paths = cls.__find(type, *args)
        if paths:
            return paths[0]

        raise FileNotFoundError("Could not find resource {0} in {1}".format(args, type))


    ##  Get the path that can be used to write a certain resource file.
    #
    #   \param type The type of resource to retrieve a path for.
    #   \param args Arguments that are appended to the location for the correct path.
    #
    #   \return A path that can be used to write the file.
    #
    #   \note This method does not check whether a given file exists.
    @classmethod
    def getStoragePath(cls, type, *args):
        return os.path.join(cls.getStoragePathForType(type), *args)

    ##  Return a list of paths for a certain resource type.
    #
    #   \param type \type{int} The type of resource to retrieve.
    #   \return \type{list} A list of absolute paths where the resource type can be found.
    #
    #   \exception TypeError Raised when type is an unknown value.
    @classmethod
    def getAllPathsForType(cls, type):
        if type not in cls.__types:
            raise TypeError("Unknown type {0}".format(type))

        paths = []

        try:
            paths.append(cls.getStoragePathForType(type))
        except UnsupportedStorageTypeError:
            pass

        for path in cls.__paths:
            paths.append(os.path.join(path, "resources", cls.__types[type]))

        return paths

    ##  Return a path where a certain resource type can be stored.
    #
    #   \param type \type{int} The type of resource to store.
    #   \return \type{string} An absolute path where the given resource type can be stored.
    #
    #   \exception UnsupportedStorageTypeError Raised when writing type is not supported.
    @classmethod
    def getStoragePathForType(cls, type):
        if type not in cls.__types_storage:
            raise UnsupportedStorageTypeError("Unknown storage type {0}".format(type))

        if cls.__config_storage_path is None or cls.__data_storage_path is None:
            cls.__initializeStoragePaths()

        path = None
        # Special casing for Linux, since config should be stored in ~/.config but data should be stored in ~/.local/share
        if type == cls.Preferences:
            path = cls.__config_storage_path
        else:
            path = os.path.join(cls.__data_storage_path, cls.__types_storage[type])

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
    def addSearchPath(cls, path):
        if os.path.isdir(path) and path not in cls.__paths:
            cls.__paths.append(path)

    ##  Remove a resource search path.
    @classmethod
    def removeSearchPath(cls, path):
        if path in cls.__paths:
            del cls.__paths[cls.__paths.index(path)]

    ##  Add a custom resource type that can be located.
    #
    #   \param type \type{int} An integer that can be used to identify the type. Should be greater than UserType.
    #   \param path \type{string} The path relative to the search paths where resources of this type can be found./
    @classmethod
    def addType(cls, type, path):
        if type in cls.__types:
            raise TypeError("Type {0} already exists".format(type))

        if type <= cls.UserType:
            raise TypeError("Type should be greater than Resources.UserType")

        cls.__types[type] = path

    ##  Add a custom storage path for a resource type.
    #
    #   \param type The type to add a storage path for.
    #   \param path The path to add as storage path. Should be relative to the resources storage path.
    @classmethod
    def addStorageType(cls, type, path):
        if type in cls.__types:
            raise TypeError("Type {0} already exists".format(type))

        cls.__types[type] = path

    ##  Remove a custom resource type.
    @classmethod
    def removeType(cls, type):
        if type not in cls.__types:
            return

        if type <= cls.UserType:
            raise TypeError("Uranium standard types cannot be removed")

        del cls.__types[type]

        if type in cls.__types_storage:
            del cls.__types_storage[type]

    ## private:

    # Returns a list of paths where args was found.
    @classmethod
    def __find(cls, type, *args):
        suffix = cls.__types.get(type, None)
        if not suffix:
            return None

        files = []
        for path in cls.__paths:
            file_path = os.path.join(path, "resources", suffix, *args)
            if os.path.exists(file_path):
                files.append(file_path)
        return files

    @classmethod
    def __initializeStoragePaths(cls):
        if platform.system() == "Windows":
            cls.__config_storage_path = os.path.join(os.path.expanduser("~/AppData/Local/"), cls.ApplicationIdentifier)
        elif platform.system() == "Darwin":
            cls.__config_storage_path = os.path.expanduser("~/.{0}".format(cls.ApplicationIdentifier))
        elif platform.system() == "Linux":
            xdg_config_home = ""
            try:
                xdg_config_home = os.environ["XDG_CONFIG_HOME"]
            except KeyError:
                xdg_config_home = os.path.expanduser("~/.config")
            cls.__config_storage_path = os.path.join(xdg_config_home, cls.ApplicationIdentifier)

            xdg_data_home = ""
            try:
                xdg_data_home = os.environ["XDG_DATA_HOME"]
            except KeyError:
                xdg_data_home = os.path.expanduser("~/.local/share")

            cls.__data_storage_path = os.path.join(xdg_data_home, cls.ApplicationIdentifier)
        else:
            cls.__config_storage_path = "."

        if not cls.__data_storage_path:
            cls.__data_storage_path = cls.__config_storage_path

    __config_storage_path = None
    __data_storage_path = None
    __paths = []
    __types = {
        Resources: "",
        Preferences: "preferences",
        Meshes: "meshes",
        Shaders: "shaders",
        i18n: "i18n",
        Images: "images",
        Themes: "themes",
        MachineDefinitions: "machines",
        MachineInstances: "machine_instances",
        Profiles: "profiles",
        MachineInstanceProfiles: "instance_profiles"
    }
    __types_storage = {
        Resources: "",
        Preferences: "",
        MachineDefinitions: "machines",
        MachineInstances: "machine_instances",
        Profiles: "profiles",
        MachineInstanceProfiles: "instance_profiles"
    }
