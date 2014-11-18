from Cura.MeshHandling.MeshWriter import MeshWriter
import time
import struct

class OBJWriter(MeshWriter):
    def __init__(self):
        super(OBJWriter, self).__init__()
        self._supported_extension = ".obj"