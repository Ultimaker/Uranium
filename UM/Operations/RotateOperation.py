# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode
from UM.Math.Vector import Vector

from . import Operation

class RotateOperation(Operation.Operation):
    """Operation that rotates a scene node."""

    def __init__(self, node, rotation, rotate_around_point = Vector(0, 0, 0)):
        """Initialises the operation.
        
        :param node: The node to rotate.
        :param rotation: A transformation quaternion that rotates a space. This
        rotation is applied on the node.
        :param kwargs: Key-word arguments, including:
        - rotate_around_point: A point around which to rotate the node.
        """

        super().__init__()
        self._node = node #The node to rotate.
        self._old_transformation = node.getLocalTransformation() #The transformation matrix before rotating, which must be restored if we undo.
        self._rotation = rotation #A rotation matrix to rotate the node with.
        self._rotate_around_point = rotate_around_point #Around what point should the rotation be done?

    def undo(self):
        """Undoes the rotation, rotating the node back."""

        self._node.setTransformation(self._old_transformation)

    def redo(self):
        """Redoes the rotation, rotating the node again."""

        self._node.setPosition(-self._rotate_around_point)
        self._node.rotate(self._rotation, SceneNode.TransformSpace.World)
        self._node.setPosition(self._rotate_around_point)

    def mergeWith(self, other):
        """Merges this operation with another RotateOperation.
        
        This prevents the user from having to undo multiple operations if they
        were not his operations.
        
        You should ONLY merge this operation with an older operation. It is NOT
        symmetric.
        
        :param other: The older RotateOperation to merge this with.
        :return: A combination of the two rotate operations.
        """

        if type(other) is not RotateOperation:
            return False
        if other._node != self._node: #Must be operations on the same node.
            return False

        op = RotateOperation(self._node, other._rotation * self._rotation)
        op._old_transformation = other._old_transformation #Use the _old_transformation of the oldest rotation in the new operation.
        return op

    def __repr__(self):
        """Returns a programmer-readable representation of this operation.
        
        :return: A programmer-readable representation of this operation.
        """

        return "RotateOp.(node={0},rot.={1})".format(self._node, self._rotation)
