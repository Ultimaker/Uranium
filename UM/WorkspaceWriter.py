from UM.PluginObject import PluginObject
class WorkspaceWriter(PluginObject):
    def __init__(self):
        self._supported_extension = ''
    
    #Tries to write to file, returns False if it's unable to do it (either due to type or due to permission / locking)
    def write(self, file_name, storage_device, scene_node):
        raise NotImplementedError('Writer plugin was not correctly implemented, no write was specified')
    
    def getSupportedExtension(self):
        return self._supported_extension