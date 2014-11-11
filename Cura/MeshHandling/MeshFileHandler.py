class MeshFileHandler(object):
    def __init__(self):
        self._mesh_readers = []
        self._mesh_writers = []
        
    def read(self, file_name):
        pass
    
    def write(self, file_name):
        pass
    
    def addWriter(self, writer):
        self._mesh_writers.append(writer)
        
    def addReader(self, reader):
        self._mesh_readers.append(reader)