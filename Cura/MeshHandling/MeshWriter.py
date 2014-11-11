class MeshWriter(object):
    def __init__(self):
        self._supported_extention = ''
    
    #Tries to write to file, returns False if it's unable to do it (either due to type or due to permission / locking)
    def write(self, file_name, mesh_data):
        raise NotImplementedError('Writer plugin was not correctly implemented, no write was specified')
    
    def getSupportedExtention(self):
        return self._supported_type