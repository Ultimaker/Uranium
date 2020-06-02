# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import Operation
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector

class SetTransformOperation(Operation.Operation):
    """Operation that translates, rotates and scales a node all at once."""

    def __init__(self, node, translation = None, orientation = None, scale = None, shear = None, mirror = None):
        """Creates the transform operation.

        Careful! No real input checking is done by this function. If you'd
        provide other transformations than respectively translation, orientation
        and scale in place for the translation, orientation and scale matrices,
        it could get confused.

        :param node: The scene node to transform.
        :param translation: A translation matrix to move the node with.
        :param orientation: An orientation matrix to rotate the node with.
        :param scale: A scaling matrix to resize the node with.
        """

        super().__init__()
        self._node = node

        self._old_translation = node.getPosition()
        self._old_orientation = node.getOrientation()
        self._old_scale = node.getScale()
        self._old_shear = node.getShear()
        self._old_transformation = node.getWorldTransformation()

        if translation:
            self._new_translation = translation
        else:
            self._new_translation = node.getPosition()

        if orientation:
            self._new_orientation = orientation
        else:
            self._new_orientation = node.getOrientation()

        if scale:
            self._new_scale = scale
        else:
            self._new_scale = node.getScale()

        if shear:
            self._new_shear = shear
        else:
            self._new_shear = node.getShear()

        self._new_mirror = Vector(1, 1, 1)
        self._new_transformation = Matrix()

        euler_orientation = self._new_orientation.toMatrix().getEuler()
        self._new_transformation.compose(scale = self._new_scale, shear = self._new_shear, angles = euler_orientation, translate = self._new_translation, mirror = self._new_mirror)

    def undo(self):
        """Undoes the transformation, restoring the node to the old state."""

        self._node.setTransformation(self._old_transformation)

    def redo(self):
        """Re-applies the transformation after it has been undone."""

        self._node.setTransformation(self._new_transformation)

    def mergeWith(self, other):
        """Merges this operation with another TransformOperation.

        This prevents the user from having to undo multiple operations if they
        were not his operations.

        You should ONLY merge this operation with an older operation. It is NOT
        symmetric.

        :param other: The older operation with which to merge this operation.
        :return: A combination of the two operations, or False if the merge
        failed.
        """

        if type(other) is not SetTransformOperation:
            return False
        if other._node != self._node: # Must be on the same node.
            return False

        op = SetTransformOperation(self._node)
        op._old_transformation = other._old_transformation
        op._new_transformation = self._new_transformation
        return op

    def __repr__(self):
        """Returns a programmer-readable representation of this operation.

        A programmer-readable representation of this operation.
        """

        return "SetTransformOp.(node={0})".format(self._node)
