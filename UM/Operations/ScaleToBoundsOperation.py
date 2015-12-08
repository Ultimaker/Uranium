# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Operations.Operation import Operation
from UM.Math.Vector import Vector
from UM.Application import Application

##  Operation subclass that will scale a node to fit within the bounds provided.
class ScaleToBoundsOperation(Operation):
    def __init__(self, node, bounds):
        super().__init__()

        #StartingPoint: get the old scale, active machine & active profile
        self._node = node
        self._old_scale = node.getScale()
        machine = Application.getInstance().getMachineManager().getActiveMachineInstance()
        profile = Application.getInstance().getMachineManager().getActiveProfile()

        #Calculate the size of the outer ribbon -> this is the outer area of the build plate where you can't print anything
        #The size is dependant on adhesion type, sizes, etc.
        outer_ribbon_size = 0.0
        adhesion_type = profile.getSettingValue("adhesion_type")
        if adhesion_type == "skirt":
            skirt_distance = profile.getSettingValue("skirt_gap")
            skirt_line_count = profile.getSettingValue("skirt_line_count")
            outer_ribbon_size = skirt_distance + (skirt_line_count * profile.getSettingValue("skirt_line_width"))
        elif adhesion_type == "brim":
            outer_ribbon_size = profile.getSettingValue("brim_width")
        elif adhesion_type == "raft":
            outer_ribbon_size = profile.getSettingValue("raft_margin") + 1

        if profile.getSettingValue("draft_shield_enabled"):
            outer_ribbon_size += profile.getSettingValue("draft_shield_dist")

        outer_ribbon_size += profile.getSettingValue("xy_offset")

        #calculate the sizes of the printable area
        printable_area_width = machine.getMachineSettingValue("machine_width") - (outer_ribbon_size * 2) - 2
        printable_area_depth = machine.getMachineSettingValue("machine_depth") - (outer_ribbon_size * 2) - 2 #substract an extra 2 because else in some cases it slightly touches the non-printable are probably rounding differences
        printable_area_height = machine.getMachineSettingValue("machine_height")

        #Get the boundingbox of the mesh and check which of its dimensions is biggest.
        bbox = self._node.getBoundingBox()
        largest_dimension = max(bbox.width, bbox.height, bbox.depth)

        #Get the maximum scale factor by dividing the size of the bounding box by the largest dimension
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