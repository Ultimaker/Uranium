# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

##  Operation that translates, rotates and scales a node all at once.
class SetTransformOperation(Operation.Operation):
    ##  Creates the transform operation.
    #
    #   Careful! No real input checking is done by this function. If you'd
    #   provide other transformations than respectively translation, orientation
    #   and scale in place for the translation, orientation and scale matrices,
    #   it could get confused.
    #
    #   \param node The scene node to transform.
    #   \param translation A translation matrix to move the node with.
    #   \param orientation An orientation matrix to rotate the node with.
    #   \param scale A scaling matrix to resize the node with.
    def __init__(self, node, translation = None, orientation = None, scale = None):
        super().__init__()
        self._node = node

        self._old_translation = node.getPosition()
        self._old_orientation = node.getOrientation()
        self._old_scale = node.getScale()

        self._new_translation = translation
        self._new_orientation = orientation
        self._new_scale = scale

    ##  Undoes the transformation, restoring the node to the old state.
    def undo(self):
        self._node.setPosition(self._old_translation)
        self._node.setOrientation(self._old_orientation)
        self._node.setScale(self._old_scale)

    ##  Re-applies the transformation after it has been undone.
    def redo(self):
        if self._new_translation:
            self._node.setPosition(self._new_translation)
        if self._new_orientation:
            self._node.setOrientation(self._new_orientation)
        if self._new_scale:
            self._node.setScale(self._new_scale)

    ##  Merges this operation with another TransformOperation.
    #
    #   This prevents the user from having to undo multiple operations if they
    #   were not his operations.
    #
    #   You should ONLY merge this operation with an older operation. It is NOT
    #   symmetric.
    #
    #   \param other The older operation with which to merge this operation.
    #   \return A combination of the two operations, or False if the merge
    #   failed.
    def mergeWith(self, other):
        if type(other) is not SetTransformOperation:
            return False

        if other._node != self._node:
            return False

        if other._new_translation is None or self._new_translation is None:
            return False

        if other._new_orientation is None or self._new_orientation is None:
            return False

        if other._new_scale is None or self._new_scale is None:
            return False

        op = SetTransformOperation(self._node, self._new_translation, self._new_orientation, self._new_scale)
        op._old_translation = other._old_translation
        op._old_orientation = other._old_orientation
        op._old_scale = other._old_scale
        return op

    ##  Returns a programmer-readable representation of this operation.
    #
    #   A programmer-readable representation of this operation.
    def __repr__(self):
        return "SetTransformOperation(node = {0})".format(self._node)
