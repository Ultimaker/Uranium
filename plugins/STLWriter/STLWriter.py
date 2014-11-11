from Cura.MeshHandling.MeshWriter import MeshWriter

class STLWriter(MeshWriter):
    def __init__(self):
        super(STLWriter, self).__init__()
        self._supported_extention = ".stl"
    
    def write(self, name, mesh_data):
        if(self._supported_extention in name):
            #TODO: add implementation
            return True
        else:
            return False