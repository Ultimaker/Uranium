# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import Operation
from UM.Scene.SceneNode import SceneNode


class MirrorOperation(Operation.Operation):
    """Operation that mirrors a scene node.

    This operation needs to store the node that was mirrored and the
    transformation matrix that performs the mirror operation itself.
    Furthermore, it allows mirroring around the center of the node's bounding
    box, or just around the coordinate system origin.
    """

    def __init__(self, node, mirror, mirror_around_center = False):
        """Initialises the operation.

        :param node: The node to mirror.
        :param mirror: A transformation matrix that mirrors the object. This
            should only define values on the diagonal of the matrix, and only the
            values 1 or -1.
        :param mirror_around_center: Whether to mirror the object around its own
            centre (True) or around the axis origin (False).
        """

        super().__init__()
        self._node = node
        self._old_transformation = node.getLocalTransformation()
        self._mirror_around_center = mirror_around_center
        self._mirror = mirror

    def undo(self):
        """Undo the operation."""

        self._node.invertNormals()
        self._node.setTransformation(self._old_transformation) #We stored the old transformation, so we can just restore that.

    def redo(self):
        """Re-apply the operation after undoing it."""

        if self._mirror_around_center: #Move the centre to the origin if we want to mirror around the centre instead of the origin.
            center = self._node.getPosition()
            self._node.setPosition(-center)
        self._node.scale(self._mirror, SceneNode.TransformSpace.World) #Then mirror around the origin.
        self._node.invertNormals()  # Because the mirror is done via a scale operation, the normals where inverted.
        if self._mirror_around_center: #If we moved the centre, move it back.
            self._node.setPosition(center)

    def mergeWith(self, other):
        """Merge this operation with another.

        This prevents the user from having to undo multiple operations if they
        were not his operations.

        You should ONLY merge this operation with an older operation. It is NOT
        symmetric.

        :param other: The operation to merge this operation with.
        :return: A combination of the two operations.
        """

        if type(other) is not MirrorOperation:
            return False
        if other._node != self._node: #Must be on the same scene node.
            return False

        op = MirrorOperation(self._node, self._mirror) #Use the entire new transformation.
        op._old_transformation = other._old_transformation #But store the old transformation from the other one.
        return op

    def __repr__(self):
        """Gives a programmer-readable representation of this operation.

        :return: A programmer-readable representation of this operation.
        """

        return "MirrorOp.(node={0},mirror={1})".format(self._node, self._mirror)
