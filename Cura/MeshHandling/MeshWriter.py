class MeshWriter(object):
    def __init__(self):
        self._supported_type = ''
    
    #Tries to write to file, returns False if it's unable to do it (either due to type or due to permission / locking)
    def write(self, file_name):
        return False
    
    def getSupportedType(self):
        return self._supported_type