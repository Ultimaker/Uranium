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
        ## Around what point should the rotation be done?
        self._rotate_around_point = kwargs.get("rotate_around_point" , Vector(0,0,0))

    def undo(self):
        self._node.setTransformation(self._old_transformation)

    def redo(self):
        self._node.setPosition(-self._rotate_around_point)
        self._node.rotate(self._rotation, SceneNode.TransformSpace.World)
        self._node.setPosition(self._rotate_around_point)

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
