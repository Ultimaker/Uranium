from UM.Qt.QtApplication import QtApplication
from UM.Scene.SceneNode import SceneNode
from UM.Resources import Resources
from UM.Math.Vector import Vector
from UM.Scene.Camera import Camera
from UM.Math.Matrix import Matrix

import os.path

class ScannerApplication(QtApplication):
    def __init__(self):
        super(ScannerApplication, self).__init__()
        self._machine_settings.loadSettingsFromFile(Resources.getPath(Resources.SettingsLocation, "ultiscantastic.json"))

        
    def run(self):
        self._plugin_registry.loadPlugins({ "type": "Logger"})
        self._plugin_registry.loadPlugins({ "type": "StorageDevice" })
        self._plugin_registry.loadPlugins({ "type": "View" })
        self._plugin_registry.loadPlugins({ "type": "MeshHandler" })
        self._plugin_registry.loadPlugins({ "type": "Tool" })
        self._plugin_registry.loadPlugin("ScannerEngineBackend")

        self.getController().setActiveView('MeshView')
        self.getController().setCameraTool("CameraTool")
        self.getController().setSelectionTool("SelectionTool")
        
        root = self.getController().getScene().getRoot()
        #TODO: hardcoded
        self.setRequiredPlugins(["ScannerEngineBackend","PLYWriter","PLYReader"])
        
        try:
            self.getMachineSettings().loadValuesFromFile(Resources.getPath(Resources.SettingsLocation, 'UltiScantastic.cfg'))
        except FileNotFoundError:
            pass
        
        self.getRenderer().setLightPosition(Vector(0, 150, 150))
        
        camera = Camera('3d', root)
        camera.translate(Vector(0, 150, 150))
        proj = Matrix()
        proj.setPerspective(45, 640/480, 1, 500)
        camera.setProjectionMatrix(proj)
        camera.setPerspective(True)
        camera.lookAt(Vector(0, 0, 0), Vector(0, 1, 0))
        
        self.getController().getScene().setActiveCamera('3d')
        
        self.setMainQml(os.path.dirname(__file__) + "/Scanner.qml")
        self.initializeEngine()
        self._plugin_registry.checkRequiredPlugins(self.getRequiredPlugins())
        if self._engine.rootObjects:
            self.exec_()
        
        