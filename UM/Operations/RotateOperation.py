from UM.Scene.SceneNode import SceneNode

from . import Operation

class RotateOperation(Operation.Operation):
    def __init__(self, node, rotation):
        super().__init__()
        self._node = node
        self._old_orientation = node.getOrientation()
        self._rotation = rotation

    def undo(self):
        self._node.setOrientation(self._old_orientation)

    def redo(self):
        self._node.rotate(self._rotation, SceneNode.TransformSpace.World)

    def mergeWith(self, other):
        if type(other) is not RotateOperation:
            return False

        if other._node != self._node:
            return False

        op = RotateOperation(self._node, other._rotation * self._rotation)
        op._old_orientation = other._old_orientation
        return op

    def __repr__(self):
        return "RotateOperation(node = {0}, rotation={1})".format(self._node, self._rotation)
