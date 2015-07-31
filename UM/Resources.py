# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import os.path
import platform
import sys

class UnknownLocationError(Exception):
    pass

class UnsupportedStorageLocationError(Exception):
    pass

class Resources:
    ResourcesLocation = 1
    SettingsLocation = 2
    PreferencesLocation = 3
    MeshesLocation = 4
    ShadersLocation = 5
    i18nLocation = 6
    ImagesLocation = 7
    ThemesLocation = 8
    FirmwareLocation = 9
    QmlFilesLocation = 10
    WizardPagesLocation = 11

    ApplicationIdentifier = "UM"

    ##  Get the path to a certain resource file
    #
    #   \param type \type{int} The type of resource to retrieve a path for.
    #   \param args Arguments that are appended to the location to locate the correct file.
    #
    #   \return A path to the file
    #
    #   \exception FileNotFoundError Raised when the file could not be found.
    @classmethod
    def getPath(cls, type, *args):
        try:
            path = os.path.join(cls.getStorageLocation(type), *args)
            if os.path.exists(path):
                return path
        except UnsupportedStorageLocationError:
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
    @classmethod
    def getStoragePath(cls, type, *args):
        return os.path.join(cls.getStorageLocation(type), *args)

    ##  Return a list of paths for a certain resource location.
    #
    #   \param type \type{int} The type of resource to retrieve.
    #   \return \type{list} A list of absolute paths where the resource type can be found.
    #
    #   \exception UnknownLocationError Raised when type is an unknown value.
    @classmethod
    def getLocation(cls, type):
        suffix = cls.__getLocationSuffix(type)
        if not suffix:
            raise UnknownLocationError("Unknown location {0}".format(type))

        locations = []
        for path in cls.__paths:
            locations.append(os.path.join(path, *suffix))

        return locations

    ##  Return a path where a certain resource type can be stored.
    #
    #   \param type \type{int} The type of resource to store.
    #   \return \type{string} An absolute path where the given resource type can be stored.
    #
    #   \exception UnsupportedStorageLocationError Raised when writing type is not supported.
    @classmethod
    def getStorageLocation(cls, type):
        if cls.__config_storage_path is None or cls.__data_storage_path is None:
            cls.__initializeStoragePaths()

        path = None
        if type == cls.PreferencesLocation:
            path = cls.__config_storage_path
        elif type == cls.SettingsLocation:
            path = os.path.join(cls.__data_storage_path, "settings")
        elif type == cls.ResourcesLocation:
            path = cls.__data_storage_path
        else:
            raise UnsupportedStorageLocationError("No known location to store type {0}".format(type))

        # Ensure the directory we want to write to exists
        try:
            os.makedirs(path)
        except OSError:
            pass

        return path

    ##  Add a path relative to which resources can be found.
    @classmethod
    def addResourcePath(cls, path):
        if os.path.isdir(path) and path not in cls.__paths:
            cls.__paths.append(path)

    ## private:

    # Returns a list of paths where args was found.
    @classmethod
    def __find(cls, type, *args):
        suffix = cls.__getLocationSuffix(type)
        if not suffix:
            return None

        files = []
        for path in cls.__paths:
            file_path = os.path.join(path, *suffix)
            file_path = os.path.join(file_path, *args)
            if os.path.exists(file_path):
                files.append(file_path)
        return files

    @classmethod
    def __getLocationSuffix(cls, type):
        if type == cls.ResourcesLocation:
            return ["resources"]
        elif type == cls.SettingsLocation:
            return ["resources", "settings"]
        elif type == cls.PreferencesLocation:
            return ["resources", "preferences"]
        elif type == cls.MeshesLocation:
            return ["resources", "meshes"]
        elif type == cls.ShadersLocation:
            return ["resources", "shaders"]
        elif type == cls.i18nLocation:
            return ["resources", "i18n"]
        elif type == cls.ImagesLocation:
            return ["resources", "images"]
        elif type == cls.ThemesLocation:
            return ["resources", "themes"]
        elif type == cls.FirmwareLocation:
            return ["resources", "firmware"]
        elif type == cls.QmlFilesLocation:
            return ["resources", "qml"]
        elif type == cls.WizardPagesLocation:
            return ["resources", "qml", "WizardPages"]
        else:
            return None

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
            cls.__config_storage_path = cls.__relativeToAppBase("")

        if not cls.__data_storage_path:
            cls.__data_storage_path = cls.__config_storage_path

    __config_storage_path = None
    __data_storage_path = None
    __paths = []
