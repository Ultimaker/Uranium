from Cura.Application import Application

class ScannerApplication(Application):
    def __init__(self):
        super(ScannerApplication, self).__init__()
        
        self._plugin_registry.loadPlugin("STLReader")
        
    def run(self):
        print("Imma scanning ma laz0rs")
