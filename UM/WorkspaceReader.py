from UM.PluginObject import PluginObject
class WorkspaceReader(PluginObject):
    def __init__(self):
        super().__init__()
        self._supported_extension = ""
    
    # Tries to read the file from specified file_name, returns None if it's uncessfull or unable to read.
    def read(self, file_name, storage_device):
        raise NotImplementedError('Reader plugin was not correctly implemented, no read was specified')
    
    def getSupportedExtension(self):
        return self._supported_extension