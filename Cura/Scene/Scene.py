from Cura.Scene.SceneNode import SceneNode
from Cura.Signal import Signal

##  Container object for the scene graph.
class Scene(object):
    def __init__(self):
        self.sceneChanged = Signal()
        
        self._root = SceneNode()
        self._root.transformationChanged.connect(self.sceneChanged)
        self._root.childrenChanged.connect(self.sceneChanged)
        self._root.meshDataChanged.connect(self.sceneChanged)
        self._active_camera = None
        
    ##  Get the root node of the scene.
    def getRoot(self):
        return self._root

    ##  Get the camera that should be used for rendering.
    def getActiveCamera(self):
        return self._active_camera

    ##  Set the camera that should be used for rendering.
    #   \param camera The camera to use.
    def setActiveCamera(self, camera):
        self._active_camera = camera

    ##  Signal. Emitted whenever something in the scene changes.
    #   \param object The object that triggered the change.
    sceneChanged = None
