from . import Operation

class RotateOperation(Operation.Operation):
    def __init__(self, node, axis, rotation):
        super().__init__()
        self._node = node
        self._old_transform = node.getLocalTransformation()
        self._axis = axis
        self._angle = rotation

    def undo(self):
        self._node.setLocalTransformation(self._old_transform)

    def redo(self):
        self._node.rotateByAngleAxis(self._angle, self._axis)

    def mergeWith(self, other):
        if type(other) is not RotateOperation:
            return False

        if other._node != self._node:
            return False

        if self._timestamp - other._timestamp > self._mergeWindow:
            return False

        op = RotateOperation(self._node, self._axis, self._angle)
        op._old_transform = other._old_transform
        return op

    def __repr__(self):
        return "TranslateOperation(node = {0}, translation={1})".format(self._node, self._translation)

    ## private:

    _mergeWindow = 0.5 #If the time between this operation and a different operation is less than this they can be merged.
