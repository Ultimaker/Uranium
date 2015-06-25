# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Operations.Operation import Operation
from UM.Math.Vector import Vector

##  Operation subclass that will scale a node to fit within the bounds provided.
class ScaleToBoundsOperation(Operation):
    def __init__(self, node, bounds):
        super().__init__()
        self._node = node
        self._old_scale = node.getScale()

        bbox = self._node.getBoundingBox()

        largest_dimension = max(bbox.width, bbox.height, bbox.depth)

        scale_factor = 1.0
        if largest_dimension == bbox.depth:
            scale_factor = self._old_scale.z * (bounds.depth / bbox.depth)
        elif largest_dimension == bbox.width:
            scale_factor = self._old_scale.x * (bounds.width / bbox.width)
        elif largest_dimension == bbox.height:
            scale_factor = self._old_scale.y * (bounds.height / bbox.height)

        self._new_scale = Vector(scale_factor, scale_factor, scale_factor)

    def undo(self):
        self._node.setScale(self._old_scale)

    def redo(self):
        self._node.setPosition(Vector(0, 0, 0))
        self._node.setScale(self._new_scale)
