class PluginError(Exception):
    def __init__(self, error = None):
        self._error = error
        
    def __str__(self):
        return self._error
    
    
class PluginNotFoundError(Exception):
    def __init__(self, name):
        self._name = name
        
    def __str__(self):
        return "Could not find plugin " + self._name