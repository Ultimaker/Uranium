from UM.Controller import Controller
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Settings.MachineSettings import MachineSettings
from UM.Resources import Resources
from UM.Operations.OperationStack import OperationStack
from UM.Event import CallFunctionEvent
from UM.Signal import Signal, SignalEmitter
from UM.WorkspaceFileHandler import WorkspaceFileHandler
from UM.Logger import Logger
from UM.Preferences import Preferences

import threading
import argparse
import os
import urllib.parse

##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
class Application(SignalEmitter):
    ## Init method
    #
    #  \param name The name of the application.
    def __init__(self, name, **kwargs):
        if(Application._instance != None):
            raise ValueError("Duplicate singleton creation")
        # If the constructor is called and there is no instance, set the instance to self. 
        # This is done because we can't make constructor private
        Application._instance = self

        Signal._app = self
        Resources.ApplicationIdentifier = name
        self._main_thread = threading.current_thread()

        super().__init__(**kwargs) # Call super to make multiple inheritence work.

        self._application_name = name
        self._renderer = None

        PluginRegistry.addType('storage_device', self.addStorageDevice)
        PluginRegistry.addType('backend', self.setBackend)
        PluginRegistry.addType('logger', Logger.addLogger)
        PluginRegistry.addType('extension', self.addExtension)

        preferences = Preferences.getInstance()
        preferences.addPreference('general/language', 'en')

        self._controller = Controller(self)
        self._mesh_file_handler = MeshFileHandler()
        self._workspace_file_handler = WorkspaceFileHandler()
        self._storage_devices = {}
        self._backend = None

        self._machines = []
        self._active_machine = None
        
        self._required_plugins = [] 

        self._operation_stack = OperationStack()

        self._plugin_registry = PluginRegistry.getInstance()
        self._plugin_registry.addPluginLocation("plugins")
        self._plugin_registry.setApplication(self)

        self._parsed_arguments = None
        self.parseArguments()
    
    ##  Function that needs to be overriden by child classes with a list of plugin it needs (see printer application & scanner application)
    def _loadPlugins(self):
        pass

    def getArgument(self, name, default = None):
        if not self._parsed_arguments:
            self.parseArguments()

        return self._parsed_arguments.get(name, default)
    
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
    def getMachines(self):
        return self._machines

    def addMachine(self, machine):
        self._machines.append(machine)
        self._machines.sort(key = lambda k: k.getName())
        self.machinesChanged.emit()
        return len(self._machines) - 1

    def removeMachine(self, machine):
        self._machines.remove(machine)

        try:
            path = Resources.getStoragePath(Resources.SettingsLocation, urllib.parse.quote_plus(machine.getName()) + '.cfg')
        except FileNotFoundError:
            pass
        else:
            os.remove(path)

        self.machinesChanged.emit()

    machinesChanged = Signal()

    def getActiveMachine(self):
        return self._active_machine

    def setActiveMachine(self, machine):
        self._active_machine = machine
        self.activeMachineChanged.emit()

    activeMachineChanged = Signal()

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
    
    ##  Get the workspace file handler of this application.
    #   The difference between this and the mesh file handler is that the workspace handler accepts a node
    #   This means that multiple meshes can be saved / loaded in this way. 
    #   \returns MeshFileHandler
    def getWorkspaceFileHandler(self):
        return self._workspace_file_handler

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
    def addStorageDevice(self, device):
        self._storage_devices[device.getPluginId()] = device

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

    def parseArguments(self):
        parser = argparse.ArgumentParser(prog = self.getApplicationName())
        parser.add_argument('--version', action='version', version='%(prog)s 1.0')
        parser.add_argument('--external-backend',
                            dest='external-backend',
                            action='store_true', default=False,
                            help='Use an externally started backend instead of starting it automatically.')

        self._parsed_arguments = vars(parser.parse_args())

    def loadMachines(self):
        settingsDir = Resources.getStorageLocation(Resources.SettingsLocation)
        for entry in os.listdir(settingsDir):
            settings = MachineSettings()
            settings.loadValuesFromFile(os.path.join(settingsDir, entry))
            self._machines.append(settings)
        self._machines.sort(key = lambda k: k.getName())

    def saveMachines(self):
        settingsDir = Resources.getStorageLocation(Resources.SettingsLocation)
        for machine in self._machines:
            machine.saveValuesToFile(os.path.join(settingsDir, urllib.parse.quote_plus(machine.getName()) + '.cfg'))

    def addExtension(self, extension):
        pass

    _instance = None
