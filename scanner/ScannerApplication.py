from Cura.Wx.WxApplication import WxApplication
from Cura.Wx.MainWindow import MainWindow
from Cura.Scene.SceneNode import SceneNode
class ScannerApplication(WxApplication):
    def __init__(self):
        super(ScannerApplication, self).__init__()
        
        self._plugin_registry.loadPlugin("STLReader")
        self._plugin_registry.loadPlugin("STLWriter")
        self._plugin_registry.loadPlugin("MeshView")
        self._plugin_registry.loadPlugin("TransformTool")
        self._plugin_registry.loadPlugins({ "type": "StorageDevice" })

        
    def run(self):
        self.getController().setActiveView("MeshView")
        root = self.getController().getScene().getRoot()
        mesh = SceneNode()
        mesh.setMeshData(self.getMeshFileHandler().read("plugins/STLReader/simpleTestCube.stl",self.getStorageDevice('local')))
        root.addChild(mesh)
        print("Imma scanning ma laz0rs")
        window = MainWindow("Cura Scanner",self)
        window.Show()
        super(ScannerApplication, self).run()
