# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode

from . import Operation
from UM.Math.Vector import Vector


class GravityOperation(Operation.Operation):
    """An operation that moves a scene node down to 0 on the y-axis.
    """

    def __init__(self, node):
        """Initialises this GravityOperation.

        :param node: The node to translate.
        """

        super().__init__()
        self._node = node
        self._old_transformation = node.getLocalTransformation() # To restore the transformation to in case of an undo.

    def undo(self):
        """Undoes the gravity operation, restoring the old transformation."""

        self._node.setTransformation(self._old_transformation)

    def redo(self):
        """(Re-)Applies the gravity operation."""

        # Drop to bottom of usable space (if not already there):
        height_move = -self._node.getBoundingBox().bottom
        if self._node.hasDecoration("getZOffset"):
            height_move += self._node.callDecoration("getZOffset")
        if abs(height_move) > 1e-5:
            self._node.translate(Vector(0.0, height_move, 0.0), SceneNode.TransformSpace.World)

    def mergeWith(self, other):
        """Merges this operation with another gravity operation.

        This prevents the user from having to undo multiple operations if they
        were not his operations.

        You should ONLY merge this operation with an older operation. It is NOT
        symmetric.

        :param other: The older gravity operation to merge this operation with.
        """

        if type(other) is not GravityOperation:
            return False
        if other._node != self._node: # Must be moving the same node.
            return False
        return other

    def __repr__(self):
        """Returns a programmer-readable representation of this operation.

        :return: A programmer-readable representation of this operation.
        """

        return "GravityOp.(node={0})".format(self._node)
