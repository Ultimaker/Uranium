from Cura.Scene.SceneObject import SceneObject
from Cura.Signal import Signal

class Scene(object):
    def __init__(self):
        self._root = SceneObject()
        
        self._active_camera = None
        
    def getRoot(self):
        return self._root

    def getActiveCamera(self):
        return self._active_camera

    def setActiveCamera(self, camera):
        self._active_camera = camera
