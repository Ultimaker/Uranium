from Cura.Controller import Controller
from Cura.PluginRegistry import PluginRegistry
from Cura.MeshHandling.MeshFileHandler import MeshFileHandler

##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
class Application(object):
    def __init__(self):
        super(Application, self).__init__()
        self._plugin_registry = PluginRegistry()
        self._plugin_registry.addPluginLocation("plugins")
        self._plugin_registry.setApplication(self)
        self._controller = Controller()
        self._mesh_file_handler = MeshFileHandler()
        self._storage_devices = {}

    ##  Get the PluginRegistry of this application.
    def getPluginRegistry(self):
        return self._plugin_registry

    ##  Get the Controller of this application.
    def getController(self):
        return self._controller

    ##  Get the MeshFileHandler of this application.
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
        pass
