from Cura.Application import Application
from Cura.MeshHandling.MeshData import MeshData

class ScannerApplication(Application):
    def __init__(self):
        super(ScannerApplication, self).__init__()
        
        self._plugin_registry.loadPlugin("STLReader")
        #self._plugin_registry.loadPlugin("STLWriter")
        self._plugin_registry.loadPlugin("MeshView")
        self._plugin_registry.loadPlugin("TransformTool")
        test_mesh = self._mesh_file_handler.read("plugins/STLReader/simpleTestCube.stl")
        print test_mesh.getNumVerts()
        
    def run(self):
        print("Imma scanning ma laz0rs")
