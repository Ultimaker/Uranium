from UM.PluginObject import PluginObject

class MeshWriter(PluginObject):
    def __init__(self):
        self._supported_extension = ''
        super().__init__()
    
    #Tries to write to file, returns False if it's unable to do it (either due to type or due to permission / locking)
    def write(self, file_name, storage_device, mesh_data):
        raise NotImplementedError('Writer plugin was not correctly implemented, no write was specified')
    
    def getSupportedExtension(self):
        return self._supported_extension