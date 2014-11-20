from Cura.MeshHandling.MeshWriter import MeshWriter

class PCDWriter(MeshWriter):
    def __init__(self):
        super(PCDWriter, self).__init__()
        self._supported_extension = ".pcd"