from Cura.Wx.WxApplication import WxApplication

class ScannerApplication(WxApplication):
    def __init__(self):
        super(ScannerApplication, self).__init__()
        
        self._plugin_registry.loadPlugin("STLReader")
        self._plugin_registry.loadPlugin("STLWriter")
        self._plugin_registry.loadPlugin("MeshView")
        self._plugin_registry.loadPlugin("TransformTool")
        
    def run(self):
        print("Imma scanning ma laz0rs")
        super(ScannerApplication, self).run()
