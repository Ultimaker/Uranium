from . import Operation

class ScaleOperation(Operation.Operation):
    def __init__(self, node, scale):
        super().__init__()
        self._node = node
        self._old_scale = node.getScale()
        self._new_scale = self._old_scale + scale

    def undo(self):
        self._node.setScale(self._old_scale)

    def redo(self):
        self._node.setScale(self._new_scale)

    def mergeWith(self, other):
        if type(other) is not ScaleOperation:
            return False

        if other._node != self._node:
            return False

        if self._timestamp - other._timestamp > self._mergeWindow:
            return False

        op = ScaleOperation(self._node, self._new_scale)
        op._old_scale = other._old_scale
        return op

    def __repr__(self):
        return "TranslateOperation(node = {0}, translation={1})".format(self._node, self._translation)

    ## private:

    _mergeWindow = 0.5 #If the time between this operation and a different operation is less than this they can be merged.
