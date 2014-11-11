class MeshFileHandler(object):
    def __init__(self):
        self._mesh_readers = []
        self._mesh_writers = []
        
    def read(self, file_name):
        for reader in self._mesh_writers:
            result = reader.read(file_name) 
            if(result is not None):
                return result
        return None #unable to read
    
    def write(self, file_name):
        for writer in self._mesh_readers:
            if(writer.write(file_name)):
                return True
        return False
    
    def addWriter(self, writer):
        self._mesh_writers.append(writer)
        
    def addReader(self, reader):
        self._mesh_readers.append(reader)