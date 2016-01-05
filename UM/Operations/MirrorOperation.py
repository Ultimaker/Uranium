# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation
from UM.Scene.SceneNode import SceneNode

class MirrorOperation(Operation.Operation):
    def __init__(self, node, mirror, **kwargs):
        super().__init__()
        self._node = node
        self._old_mirror = node.getMirror()
        self._set_mirror = kwargs.get("set_mirror", False)
        self._mirror = mirror

    def undo(self):
        self._node.setMirror(self._old_mirror)

    def redo(self):
        if self._set_mirror:
            self._node.setMirror(self._mirror)
        else:
            self._node.mirror(self._mirror, SceneNode.TransformSpace.World)

    def mergeWith(self, other):
        if type(other) is not MirrorOperation:
            return False

        if other._node != self._node:
            return False

        if other._set_mirror and not self._set_mirror:
            return False

        op = MirrorOperation(self._node, self._mirror)
        op._old_scale = other._old_scale
        return op

    def __repr__(self):
        return "MirrorOperation(node = {0}, mirror={1})".format(self._node, self._mirror)

