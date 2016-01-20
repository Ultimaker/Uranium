# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import Operation

class SetTransformOperation(Operation.Operation):
    def __init__(self, node, translation = None, orientation = None, scale = None):
        super().__init__()
        self._node = node

        self._old_translation = node.getPosition()
        self._old_orientation = node.getOrientation()
        self._old_scale = node.getScale()

        self._new_translation = translation
        self._new_orientation = orientation
        self._new_scale = scale

    def undo(self):
        self._node.setPosition(self._old_translation)
        self._node.setOrientation(self._old_orientation)
        self._node.setScale(self._old_scale)

    def redo(self):
        if self._new_translation:
            self._node.setPosition(self._new_translation)
        if self._new_orientation:
            self._node.setOrientation(self._new_orientation)
        if self._new_scale:
            self._node.setScale(self._new_scale)

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

    def __repr__(self):
        return "SetTransformOperation(node = {0})".format(self._node)
