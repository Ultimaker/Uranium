from Cura.MeshHandling.MeshReader import MeshReader
from Cura.MeshHandling.MeshData import MeshData

class STLReader(MeshReader):
    def __init__(self):
        super(STLReader, self).__init__()
        self._supported_extension = ".stl"
    
    def read(self, name):
        if(self._supported_extension in name):
            #TODO: Add implementation
            return MeshData()
        else:
            return None
    