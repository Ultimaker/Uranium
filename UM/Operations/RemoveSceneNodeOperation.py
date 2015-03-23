from . import Operation

from UM.Scene.SceneNode import SceneNode

##  An operation that removes an list of SceneNode from the scene.
class RemoveSceneNodeOperation(Operation.Operation):
    def __init__(self, node):
        super().__init__()
        self._node = node
        self._parent = node.getParent()

    def undo(self):
        self._node.setParent(self._parent)

    def redo(self):
        self._node.setParent(None)
