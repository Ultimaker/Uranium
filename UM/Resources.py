import os
import os.path
import platform

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

    ApplicationIdentifier = 'UM'

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
            if os.path.isfile(path):
                return path
        except UnsupportedStorageLocationError:
            pass

        path = os.path.join(cls.getLocation(type), *args)
        if os.path.isfile(path):
            return path

        raise FileNotFoundError('Could not find resource {0} in {1}'.format(args, type))


    ##  Get the path that can be used to write a certain resource file.
    #
    #   \param type The type of resource to retrieve a path for.
    #   \param args Arguments that are appended to the location for the correct path.
    #
    #   \return A path that can be used to write the file.
    @classmethod
    def getStoragePath(cls, type, *args):
        return os.path.join(cls.getStorageLocation(type), *args)

    ##  Return a path for a certain resource location.
    #
    #   \param type \type{int} The type of resource to retrieve.
    #   \return \type{string} An absolute path where the resource type can be found.
    #
    #   \exception UnknownLocationError Raised when type is an unknown value.
    @classmethod
    def getLocation(cls, type):
        if type == cls.ResourcesLocation:
            return cls.__relativeToFile("..", "resources")
        elif type == cls.SettingsLocation:
            return cls.__relativeToFile("..", "resources", "settings")
        elif type == cls.PreferencesLocation:
            return cls.__relativeToFile("..", "resources", "preferences")
        elif type == cls.MeshesLocation:
            return cls.__relativeToFile("..", "resources", "meshes")
        elif type == cls.ShadersLocation:
            return cls.__relativeToFile("..", "resources", "shaders")
        elif type == cls.i18nLocation:
            return cls.__relativeToFile("..", "resources", "i18n")
        elif type == cls.ImagesLocation:
            return cls.__relativeToFile("..", "resources", "images")
        else:
            raise UnknownLocationError("Unknonw location {0}".format(cls.type))

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
            path = os.path.join(cls.__data_storage_path, 'settings')
        else:
            raise UnsupportedStorageLocationError('No known location to store type {0}'.format(type))

        # Ensure the directory we want to write to exists
        try:
            os.makedirs(path)
        except OSError:
            pass

        return path

    ##  Return the location of an icon by name.
    #
    #   \param name \type{string} The name of the icon.
    #   \return \type{string} The location of the icon.
    #
    #   \todo Move this to Theme once we implement that.
    @classmethod
    def getIcon(cls, name):
        try:
            return cls.getPath(cls.ResourcesLocation, 'icons', name)
        except FileNotFoundError:
            return os.path.join(cls.getPath(cls.ResourcesLocation), 'icons', 'default.png')

    ## private:

    # Return a path relative to this file.
    @classmethod
    def __relativeToFile(cls, *args):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), *args)

    @classmethod
    def __initializeStoragePaths(cls):
        if platform.system() == 'Windows':
            cls.__config_storage_path = os.path.join(os.path.expanduser('~/AppData/Local/'), cls.ApplicationIdentifier)
        elif platform.system() == 'Darwin':
            cls.__config_storage_path = os.path.expanduser('~/.{0}'.format(cls.ApplicationIdentifier))
        elif platform.system() == 'Linux':
            xdg_config_home = ''
            try:
                xdg_config_home = os.environ['XDG_CONFIG_HOME']
            except KeyError:
                xdg_config_home = os.path.expanduser('~/.config')
            cls.__config_storage_path = os.path.join(xdg_config_home, cls.ApplicationIdentifier)

            xdg_data_home = ''
            try:
                xdg_data_home = os.environ['XDG_DATA_HOME']
            except KeyError:
                xdg_data_home = os.path.expanduser('~/.local/share')

            cls.__data_storage_path = os.path.join(xdg_data_home, cls.ApplicationIdentifier)
        else:
            cls.__config_storage_path = cls.__relativeToFile('..')

        if not cls.__data_storage_path:
            cls.__data_storage_path = cls.__config_storage_path

    __config_storage_path = None
    __data_storage_path = None

