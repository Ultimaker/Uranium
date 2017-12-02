# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

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

    def buildMesh(self):
        #SOLIDMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            color = self._z_axis_color
        )

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = self._y_axis_color
        )

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = self._x_axis_color
        )
        self.setSolidMesh(mb.build())

        #SELECTIONMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            color = ToolHandle.ZAxisSelectionColor
        )

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = ToolHandle.YAxisSelectionColor
        )

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = ToolHandle.XAxisSelectionColor
        )

        self.setSelectionMesh(mb.build())
