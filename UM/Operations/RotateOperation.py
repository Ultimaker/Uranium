# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector

from . import Operation

class RotateOperation(Operation.Operation):
    def __init__(self, node, rotation, **kwargs):
        super().__init__()
        self._node = node
        self._old_transformation = node.getLocalTransformation()
        self._rotation = rotation

        self._rotate_around_center = kwargs.get("rotate_around_center", False)

    def undo(self):
        self._node.setTransformation(self._old_transformation)

    def redo(self):
        if self._rotate_around_center:
            center = self._node.getBoundingBox().center
            self._node.setPosition(-center)
        self._node.rotate(self._rotation, SceneNode.TransformSpace.World)
        if self._rotate_around_center:
            self._node.setPosition(center)

    def mergeWith(self, other):
        if type(other) is not RotateOperation:
            return False

        if other._node != self._node:
            return False

        op = RotateOperation(self._node, other._rotation * self._rotation)
        op._old_transformation = other._old_transformation
        return op

    def __repr__(self):
        return "RotateOperation(node = {0}, rotation={1})".format(self._node, self._rotation)
