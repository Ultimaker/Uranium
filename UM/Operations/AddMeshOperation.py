from . import Operation

from UM.Scene.SceneNode import SceneNode

class AddMeshOperation(Operation.Operation):
    def __init__(self, mesh, parent):
        super().__init__()
        self._node = None
        self._mesh = mesh
        self._parent = parent

    def undo(self):
        self._node.setParent(None)

    def redo(self):
        if not self._node:
            self._node = SceneNode()
            self._node.setMeshData(self._mesh)
            self._node.setSelectionMask(1)

        self._node.setParent(self._parent)
