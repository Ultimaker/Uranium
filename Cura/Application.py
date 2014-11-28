from Cura.Controller import Controller
from Cura.PluginRegistry import PluginRegistry
from Cura.MeshHandling.MeshFileHandler import MeshFileHandler
from Cura.Settings.MachineSettings import MachineSettings

##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
class Application(object):
    def __init__(self):
        super(Application, self).__init__() # Call super to make multiple inheritence work.
        self._plugin_registry = PluginRegistry()
        self._plugin_registry.addPluginLocation("plugins")
        self._plugin_registry.setApplication(self)
        self._controller = Controller(self)
        self._mesh_file_handler = MeshFileHandler()
        self._storage_devices = {}
        self._loggers = []
        self._backend = None
        self._machine_settings = MachineSettings()
        self._machine_settings.loadSettingsFromFile("tests/Settings/SettingData.json") #TODO: Debug code
    
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

    ##  Add a logger to the list.
    #   \param logger Logger
    def addLogger(self, logger):
        self._loggers.append(logger)
    
    ##  Get all loggers
    #   \returns List of Loggers
    def getLoggers(self):
        return self._loggers

    ##  Send a message of certain type to all loggers to be handled.
    #   \param log_type 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning)
    #   \param message String containing message to be logged
    #   \param message List of variables to be added to the message
    def log(self, log_type, message, *args):
        for logger in self._loggers:
            filled_message = message % args # Replace all the %s with the variables. Python formating is magic.
            logger.log(log_type, filled_message)

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
