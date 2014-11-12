from Cura.Wx.WxApplication import WxApplication
from Cura.Wx.MainWindow import MainWindow

class ScannerApplication(WxApplication):
    def __init__(self):
        super(ScannerApplication, self).__init__()
        
        self._plugin_registry.loadPlugin("STLReader")
        self._plugin_registry.loadPlugin("STLWriter")
        self._plugin_registry.loadPlugin("MeshView")
        self._plugin_registry.loadPlugin("TransformTool")
        test_mesh = self._mesh_file_handler.read("plugins/STLReader/simpleTestCube.stl")
        
    def run(self):
        print("Imma scanning ma laz0rs")
        window = MainWindow("Cura Scanner")
        window.Show()
        super(ScannerApplication, self).run()
