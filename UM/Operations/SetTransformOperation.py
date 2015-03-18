from . import Operation

class SetTransformOperation(Operation.Operation):
    def __init__(self, node, transform):
        super().__init__()
        self._node = node
        self._old_transform = node.getLocalTransformation()
        self._new_transform = transform

    def undo(self):
        self._node.setLocalTransformation(self._old_transform)

    def redo(self):
        self._node.setLocalTransformation(self._new_transform)

    def mergeWith(self, other):
        if type(other) is not SetTransformOperation:
            return False

        if other._node != self._node:
            return False

        op = SetTransformOperation(self._node, self._new_transform)
        op._old_transform = other._old_transform
        return op

    def __repr__(self):
        return "SetTransformOperation(node = {0}, old_transform={1}, new_transform={2})".format(self._node, self._old_transform, self._new_transform)
