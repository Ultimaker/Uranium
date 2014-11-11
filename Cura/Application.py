
from Cura.Controller import Controller
from Cura.PluginRegistry import PluginRegistry
from Cura.MeshHandling.MeshFileHandler import MeshFileHandler

class Application(object):
    def __init__(self):
        self._plugin_registry = PluginRegistry()
        self._plugin_registry.addPluginLocation("plugins")
        self._plugin_registry.setApplication(self)
        self._controller = Controller()
        self._mesh_file_handler = MeshFileHandler()
        
    def getPluginRegistry(self):
        return self._plugin_registry

    def getController(self):
        return self._controller
    
    def getMeshFileHandler(self):
        return self._mesh_file_handler
    
    def run(self):
        pass
