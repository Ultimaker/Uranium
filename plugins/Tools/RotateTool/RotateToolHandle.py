# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

import math

##  Provides the circular toolhandles for each axis for the rotate tool

class RotateToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._inner_radius = 40
        self._outer_radius = 40.5
        self._line_width = 0.5
        self._active_inner_radius = 37
        self._active_outer_radius = 44
        self._active_line_width = 3

        #SOLIDMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            color = ToolHandle.ZAxisColor
        )

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = ToolHandle.YAxisColor
        )

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = ToolHandle.XAxisColor
        )
        self.setSolidMesh(mb.build())

        #SELECTIONMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            color = ToolHandle.ZAxisColor
        )

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = ToolHandle.YAxisColor
        )

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = ToolHandle.XAxisColor
        )

        self.setSelectionMesh(mb.build())
