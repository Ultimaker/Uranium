import os.path

class Resources:
    ResourcesLocation = 1
    SettingsLocation = 2
    PreferencesLocation = 3
    MeshesLocation = 4

    @classmethod
    def locate(cls, type, *args):
        path = os.path.join(cls.getPath(type), *args)
        if os.path.isfile(path):
            return path

        return ''

    ##  Return a path to read a certain resource type from.
    #
    #   \param type \type{int} The type of resource to retrieve.
    #   \return \type{string} An absolute path where the resource type can be found.
    #
    #   \exception ValueError Raised when type is an unknown value.
    @classmethod
    def getPath(cls, type):
        if type == cls.ResourcesLocation:
            return cls.__relativeToFile("..", "resources")
        elif type == cls.SettingsLocation:
            return cls.__relativeToFile("..", "resources", "settings")
        elif type == cls.PreferencesLocation:
            return cls.__relativeToFile("..", "resources", "preferences")
        elif type == cls.MeshesLocation:
            return cls.__relativeToFile("..", "resources", "meshes")
        else:
            raise ValueError("Unknonw location {0}".format(type))

    ##  Return a path where a certain resource type can be stored.
    #
    #   \param type \type{int} The type of resource to store.
    #   \return \type{string} An absolute path where the given resource type can be stored.
    #
    #   \exception ValueError Raised when type is an unknown value.
    @classmethod
    def getStoragePath(cls, type):
        pass

    ##  Return the location of an icon by name.
    #
    #   \param name \type{string} The name of the icon.
    #   \return \type{string} The location of the icon.
    #
    #   \todo Move this to Theme once we implement that.
    @classmethod
    def getIcon(cls, name):
        path = os.path.join(cls.getPath(cls.ResourcesLocation), 'icons', name)
        if os.path.isfile(path):
            return path
        else:
            return os.path.join(cls.getPath(cls.ResourcesLocation), 'icons', 'default.png')

    ## private:

    # Return a path relative to this file.
    @classmethod
    def __relativeToFile(cls, *args):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), *args)
