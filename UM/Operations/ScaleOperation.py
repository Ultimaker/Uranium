from . import Operation

class ScaleOperation(Operation.Operation):
    def __init__(self, node, scale, **kwargs):
        super().__init__()
        self._node = node
        self._old_scale = node.getScale()
        self._set_scale = kwargs.get("set_scale", False)
        self._scale = scale

    def undo(self):
        self._node.setScale(self._old_scale)

    def redo(self):
        if self._set_scale:
            self._node.setScale(self._scale)
        else:
            self._node.scale(self._scale)

    def mergeWith(self, other):
        if type(other) is not ScaleOperation:
            return False

        if other._node != self._node:
            return False

        if other._set_scale and not self._set_scale:
            return False

        op = ScaleOperation(self._node, self._scale)
        op._old_scale = other._old_scale
        return op

    def __repr__(self):
        return "ScaleOperation(node = {0}, scale={1})".format(self._node, self._new_scale)

