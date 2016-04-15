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

        scale_factor = min(bounds.width / bbox.width,  bounds.height /bbox.height, bounds.depth / bbox.depth)

        #Aply scale factor on all different sizes to respect the (non-uniform) scaling that already has been done by the user
        self._new_scale = Vector(self._old_scale.x * scale_factor, self._old_scale.y * scale_factor, self._old_scale.z * scale_factor)

    def undo(self):
        self._node.setScale(self._old_scale)

    def redo(self):
        self._node.setScale(self._new_scale)