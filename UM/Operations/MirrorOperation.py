# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation
from UM.Scene.SceneNode import SceneNode

class MirrorOperation(Operation.Operation):
    def __init__(self, node, mirror, **kwargs):
        super().__init__()
        self._node = node
        self._old_transformation = node.getLocalTransformation()
        self._mirror = mirror

    def undo(self):
        self._node.setTransformation(self._old_transformation)

    def redo(self):
        self._node.scale(self._mirror, SceneNode.TransformSpace.World)

    def mergeWith(self, other):
        if type(other) is not MirrorOperation:
            return False

        if other._node != self._node:
            return False

        op = MirrorOperation(self._node, self._mirror)
        op._old_transformation = other._old_transformation
        return op

    def __repr__(self):
        return "MirrorOperation(node = {0}, mirror={1})".format(self._node, self._mirror)

