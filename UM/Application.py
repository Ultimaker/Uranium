from UM.Controller import Controller
from UM.PluginRegistry import PluginRegistry
from UM.MeshHandling.MeshFileHandler import MeshFileHandler
from UM.Settings.MachineSettings import MachineSettings
from UM.Resources import Resources

##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
class Application(object):
    def __init__(self):
        if(Application._instance != None):
            raise ValueError("Duplicate singleton creation")

        super(Application, self).__init__() # Call super to make multiple inheritence work.
        self._plugin_registry = PluginRegistry()
        self._plugin_registry.addPluginLocation("plugins")
        self._plugin_registry.setApplication(self)
        self._controller = Controller(self)
        self._mesh_file_handler = MeshFileHandler()
        self._storage_devices = {}
        self._backend = None

        #TODO: This needs to be loaded from preferences
        self._machine_settings = MachineSettings()
        self._machine_settings.loadSettingsFromFile(Resources.getPath(Resources.SettingsLocation, "ultimaker2.json"))
    
    ##  Set the backend of the application (the program that does the heavy lifting).
    #   \param backend Backend
    def setBackend(self, backend):
        self._backend = backend
    
    ##  Get reference of the machine settings object
    #   \returns machine_settings
    def getMachineSettings(self):
        return self._machine_settings
    
    ##  Get the backend of the application (the program that does the heavy lifting).
    #   \returns Backend
    def getBackend(self):
        return self._backend

    ##  Get the PluginRegistry of this application.
    #   \returns PluginRegistry
    def getPluginRegistry(self):
        return self._plugin_registry

    ##  Get the Controller of this application.
    #   \returns Controller
    def getController(self):
        return self._controller

    ##  Get the MeshFileHandler of this application.
    #   \returns MeshFileHandler
    def getMeshFileHandler(self):
        return self._mesh_file_handler

    ##  Get a StorageDevice object by name
    #   \param name The name of the StorageDevice to get.
    #   \return The named StorageDevice or None if not found.
    def getStorageDevice(self, name):
        try:
            return self._storage_devices[name]
        except KeyError:
            return None

    ##  Add a StorageDevice
    #   \param name The name to use to identify the device.
    #   \param device The device to add.
    def addStorageDevice(self, name, device):
        self._storage_devices[name] = device

    ##  Remove a StorageDevice
    #   \param name The name of the StorageDevice to remove.
    def removeStorageDevice(self, name):
        try:
            del self._storage_devices[name]
        except KeyError:
            pass

    ##  Run the main eventloop.
    #   This method should be reimplemented by subclasses to start the main event loop.
    def run(self):
        raise NotImplementedError("Run must be implemented by application")

    ##  Return an application-specific Renderer object.
    def getRenderer(self):
        raise NotImplementedError("getRenderer must be implemented by subclasses.")

    ##  Return the singleton instance of the application object
    @classmethod
    def getInstance(cls):
        # Note: Explicit use of class name to prevent issues with inheritance.
        if Application._instance is None:
            Application._instance = cls()

        return Application._instance

    _instance = None
