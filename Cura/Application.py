
import PluginRegistry
import Controller
from MeshHandling.MeshFileHandler import MeshFileHandler

class Application(object):
    def __init__(self):
        self._plugin_registry = PluginRegistry()
        self._controller = Controller()
        self._mesh_file_handler = MeshFileHandler()
        
    def getPluginRegistry(self):
        return self._plugin_registry

    def getController(self):
        return self._controller
    
    def getMeshFileHanlder(self):
        return self._mesh_file_handler
    
    def run(self):
        pass