from Cura.Scene.SceneNode import SceneNode
from Cura.Scene.Camera import Camera
from Cura.Signal import Signal, SignalEmitter

##  Container object for the scene graph.
class Scene(SignalEmitter):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritence work.

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
    #   \param name The name of the camera to use.
    def setActiveCamera(self, name):
        camera = self._findCamera(name)
        if camera:
            self._active_camera = camera

    ##  Signal. Emitted whenever something in the scene changes.
    #   \param object The object that triggered the change.
    sceneChanged = Signal()

    def _findCamera(self, name):
        for node in self._root.getChildren():
            if type(node) is Camera and node.getName() == name:
                return node
