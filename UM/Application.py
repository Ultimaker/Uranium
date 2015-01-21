from UM.Controller import Controller
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Settings.MachineSettings import MachineSettings
from UM.Resources import Resources
from UM.Operations.OperationStack import OperationStack
from UM.Event import CallFunctionEvent
from UM.Signal import Signal

import threading

##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
class Application:
    def __init__(self):
        if(Application._instance != None):
            raise ValueError("Duplicate singleton creation")
        # If the constructor is called and there is no instance, set the instance to self. 
        # This is done because we can't make constructor private
        Application._instance = self

        Signal._app = self

        super().__init__() # Call super to make multiple inheritence work.

        self._application_name = "application"

        self._plugin_registry = PluginRegistry()
        self._plugin_registry.addPluginLocation("plugins")
        self._plugin_registry.setApplication(self)
        self._controller = Controller(self)
        self._mesh_file_handler = MeshFileHandler()
        self._storage_devices = {}
        self._backend = None

        self._machine_settings = MachineSettings()
        
        self._required_plugins = [] 

        self._operation_stack = OperationStack()

        self._main_thread = threading.current_thread()

    def getApplicationName(self):
        return self._application_name

    def setApplicationName(self, name):
        self._application_name = name
        
    ##  Application has a list of plugins that it *must* have. If it does not have these, it cannot function.
    #   These plugins can not be disabled in any way.
    def getRequiredPlugins(self):
        return self._required_plugins
    
    ##  Set the plugins that the application *must* have in order to function.
    #   \param plugin_names List of strings with the names of the required plugins
    def setRequiredPlugins(self, plugin_names):
        self._required_plugins = plugin_names

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

    def getOperationStack(self):
        return self._operation_stack

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

    ##  Post a function event onto the event loop.
    #
    #   This takes a CallFunctionEvent object and puts it into the actual event loop.
    def functionEvent(self, event):
        raise NotImplementedError("postEvent must be implemented by subclasses.")

    ##  Get the application's main thread.
    def getMainThread(self):
        return self._main_thread

    ##  Return the singleton instance of the application object
    @classmethod
    def getInstance(cls):
        # Note: Explicit use of class name to prevent issues with inheritance.
        if Application._instance is None:
            Application._instance = cls()

        return Application._instance

    _instance = None
