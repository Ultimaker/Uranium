# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Operations.Operation import Operation
from UM.Math.Vector import Vector

##  Operation subclass that will scale a node to fit within the bounds provided.
class ScaleToBoundsOperation(Operation):
    def __init__(self, node, bounds):
        super().__init__()

        #StartingPoint: get the old scale, boundingbox and largest dimension
        self._node = node
        self._old_scale = node.getScale()

        #Get the sizes of the boundingbox but substract the disallowed area's
        bbox = self._node.getBoundingBox()
        printable_area_width = bounds.width
        printable_area_depth  =  bounds.depth
        printable_area_height = bounds.height
        largest_dimension = max(bbox.width, bbox.height, bbox.depth)

        #Get the maximum scale factor by deviding the the size of the bounding box by the largest dimension
        scale_factor = 1.0
        if largest_dimension == bbox.depth:
            scale_factor = printable_area_depth / bbox.depth
        elif largest_dimension == bbox.width:
            scale_factor = printable_area_width / bbox.width
        elif largest_dimension == bbox.height:
            scale_factor = printable_area_height / bbox.height

        #Aplly scale factor on all different sizes to respect the (non-uniform) scaling that already has been done by the user
        self._new_scale = Vector(self._old_scale.x * scale_factor, self._old_scale.y * scale_factor, self._old_scale.z * scale_factor)


    def undo(self):
        self._node.setScale(self._old_scale)

    def redo(self):
        self._node.setPosition(Vector(0, 0, 0))
        self._node.setScale(self._new_scale)