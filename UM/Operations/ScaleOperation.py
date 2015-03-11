from . import Operation

class ScaleOperation(Operation.Operation):
    def __init__(self, node, scale, **kwargs):
        super().__init__()
        self._node = node
        self._old_scale = node.getScale()
        if kwargs.get('set_scale', False):
            self._new_scale = scale
        else:
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

        op = ScaleOperation(self._node, self._new_scale)
        op._old_scale = other._old_scale
        return op

    def __repr__(self):
        return "ScaleOperation(node = {0}, scale={1})".format(self._node, self._new_scale)

