from Cura.MeshHandling.MeshReader import MeshReader
from Cura.MeshHandling.MeshData import MeshData

class PCDReader(MeshReader):
    def __init__(self):
        super(PCDReader, self).__init__()
        self._supported_extension = ".pcd"