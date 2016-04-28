# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector

from . import Operation

##  Operation that rotates a scene node.
class RotateOperation(Operation.Operation):
    ##  Initialises the operation.
    #
    #   \param node The node to rotate.
    #   \param rotation A transformation matrix that rotates a space. This
    #   rotation is applied on the node.
    #   \param kwargs Key-word arguments, including:
    #     - rotate_around_point: A point around which to rotate the node.
    def __init__(self, node, rotation, rotate_around_point = Vector(0, 0, 0)):
        super().__init__()
        self._node = node #The node to rotate.
        self._old_transformation = node.getLocalTransformation() #The transformation matrix before rotating, which must be restored if we undo.
        self._rotation = rotation #A rotation matrix to rotate the node with.
        self._rotate_around_point = rotate_around_point #Around what point should the rotation be done?

    ##  Undoes the rotation, rotating the node back.
    def undo(self):
        self._node.setTransformation(self._old_transformation)

    ##  Redoes the rotation, rotating the node again.
    def redo(self):
        self._node.setPosition(-self._rotate_around_point)
        self._node.rotate(self._rotation, SceneNode.TransformSpace.World)
        self._node.setPosition(self._rotate_around_point)

    ##  Merges this operation with another RotateOperation.
    #
    #   This prevents the user from having to undo multiple operations if they
    #   were not his operations.
    #
    #   You should ONLY merge this operation with an older operation. It is NOT
    #   symmetric.
    #
    #   \param other The older RotateOperation to merge this with.
    #   \return A combination of the two rotate operations.
    def mergeWith(self, other):
        if type(other) is not RotateOperation:
            return False
        if other._node != self._node: #Must be operations on the same node.
            return False

        op = RotateOperation(self._node, other._rotation * self._rotation)
        op._old_transformation = other._old_transformation #Use the _old_transformation of the oldest rotation in the new operation.
        return op

    ##  Returns a programmer-readable representation of this operation.
    #
    #   \return A programmer-readable representation of this operation.
    def __repr__(self):
        return "RotateOperation(node = {0}, rotation={1})".format(self._node, self._rotation)
