
import PluginRegistry
import Controller

class Application(object):
    def __init__(self):
        self._plugin_registry = PluginRegistry()
        self._controller = Controller()
        
    def getPluginRegistry(self):
        return self._plugin_registry

    def getController(self):
        return self._controller
    
    def run(self):
        pass