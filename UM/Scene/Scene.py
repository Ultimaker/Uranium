from UM.Scene.SceneNode import SceneNode
from UM.Scene.Camera import Camera
from UM.Signal import Signal, SignalEmitter
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator

##  Container object for the scene graph.
#
#   The main purpose of this class is to provide the root SceneNode.
class Scene(SignalEmitter):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritence work.

        self._root = SceneNode()
        self._connectSignalsRoot()
        self._active_camera = None
    
    def _connectSignalsRoot(self):
        self._root.transformationChanged.connect(self.sceneChanged)
        self._root.childrenChanged.connect(self.sceneChanged)
        self._root.meshDataChanged.connect(self.sceneChanged)
    
    ##  Get the root node of the scene.
    def getRoot(self):
        return self._root
    
    ##  Change the root node of the scene
    def setRoot(self, node):
        self._root = node
        self._connectSignalsRoot()
        self.rootChanged.emit()
        
    rootChanged = Signal()

    ##  Get the camera that should be used for rendering.
    def getActiveCamera(self):
        return self._active_camera

    def getAllCameras(self):
        cameras = []
        for node in BreadthFirstIterator(self._root):
            if type(node) is Camera:
                cameras.append(node)

        return cameras

    ##  Set the camera that should be used for rendering.
    #   \param name The name of the camera to use.
    def setActiveCamera(self, name):
        camera = self._findCamera(name)
        if camera:
            self._active_camera = camera

    ##  Signal. Emitted whenever something in the scene changes.
    #   \param object The object that triggered the change.
    sceneChanged = Signal()

    ## private:
    def _findCamera(self, name):
        for node in BreadthFirstIterator(self._root):
            if type(node) is Camera and node.getName() == name:
                return node
