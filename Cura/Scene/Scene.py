from Cura.Scene.SceneObject import SceneObject
from Cura.Signal import Signal

class Scene(object):
    def __init__(self):
        self.sceneChanged = Signal()
        
        self._root = SceneObject()
        self._root.transformationChanged.connect(self.sceneChanged)
        self._root.childrenChanged.connect(self.sceneChanged)
        self._root.meshDataChanged.connect(self.sceneChanged)
        self._active_camera = None
        
    def getRoot(self):
        return self._root

    def getActiveCamera(self):
        return self._active_camera

    def setActiveCamera(self, camera):
        self._active_camera = camera

    ##  Signal. Emitted whenever something in the scene changes.
    #   \param object The object that triggered the change.
    sceneChanged = None
