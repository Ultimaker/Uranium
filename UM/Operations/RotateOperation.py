from . import Operation

class RotateOperation(Operation.Operation):
    def __init__(self, node, rotation):
        super().__init__()
        self._node = node
        self._old_transform = node.getLocalTransformation()
        self._rotation = rotation

    def undo(self):
        self._node.setLocalTransformation(self._old_transform)

    def redo(self):
        self._node.rotateGlobal(self._rotation)

    def mergeWith(self, other):
        if type(other) is not RotateOperation:
            return False

        if other._node != self._node:
            return False

        op = RotateOperation(self._node, self._rotation)
        op._old_transform = other._old_transform
        return op

    def __repr__(self):
        return "RotateOperation(node = {0}, rotation={1})".format(self._node, self._rotation)
