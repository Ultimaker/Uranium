from . import Operation

from UM.Scene.SceneNode import SceneNode

class AddSceneNodeOperation(Operation.Operation):
    def __init__(self, node, parent):
        super().__init__()
        self._node = node
        self._parent = parent

    def undo(self):
        self._node.setParent(None)

    def redo(self):
        self._node.setParent(self._parent)
