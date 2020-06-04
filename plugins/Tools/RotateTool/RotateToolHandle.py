# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import math
from enum import IntEnum

from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Scene.ToolHandle import ToolHandle


class RotateToolHandle(ToolHandle):
    """Provides the circular toolhandles for each axis for the rotate tool"""

    class ExtraWidgets(IntEnum):
        XPositive90 = ToolHandle.AllAxis + 1
        XNegative90 = ToolHandle.AllAxis + 2
        YPositive90 = ToolHandle.AllAxis + 3
        YNegative90 = ToolHandle.AllAxis + 4
        ZPositive90 = ToolHandle.AllAxis + 5
        ZNegative90 = ToolHandle.AllAxis + 6

    def __init__(self, parent = None):
        super().__init__(parent)

        self._name = "RotateToolHandle"
        self._inner_radius = 40
        self._outer_radius = 40.5
        self._line_width = 0.5
        self._active_inner_radius = 37
        self._active_outer_radius = 44
        self._active_line_width = 3

        self._angle_offset = 3
        self._handle_offset_a = self._inner_radius * math.cos(math.radians(self._angle_offset))
        self._handle_offset_b = self._inner_radius * math.sin(math.radians(self._angle_offset))

        self._handle_height = 7
        self._handle_width = 3
        self._active_handle_height = 9
        self._active_handle_width = 7

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

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(0, self._handle_offset_a, -self._handle_offset_b),
            color = self._x_axis_color,
            axis = Vector.Unit_X,
            angle = 90 + self._angle_offset
        )
        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(0, self._handle_offset_a, self._handle_offset_b),
            color = self._x_axis_color,
            axis = Vector.Unit_X,
            angle = -90 - self._angle_offset
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(self._handle_offset_b, 0, self._handle_offset_a),
            color = self._y_axis_color,
            axis = Vector.Unit_Z,
            angle = 90 - self._angle_offset
        )
        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(-self._handle_offset_b, 0, self._handle_offset_a),
            color = self._y_axis_color,
            axis = Vector.Unit_Z,
            angle = -90 + self._angle_offset
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(self._handle_offset_a, self._handle_offset_b, 0),
            color = self._z_axis_color,
            axis = Vector.Unit_Z,
            angle = - self._angle_offset
        )
        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(self._handle_offset_a, -self._handle_offset_b, 0),
            color = self._z_axis_color,
            axis = Vector.Unit_Z,
            angle = 180 + self._angle_offset
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

        mb.addPyramid(
            width = self._active_handle_width,
            height = self._active_handle_height,
            depth = self._active_handle_width,
            center = Vector(0, self._handle_offset_a, self._handle_offset_b),
            color = self._extra_widgets_color_map[self.ExtraWidgets.XPositive90.value],
            axis = Vector.Unit_X,
            angle = -90 - self._angle_offset
        )
        mb.addPyramid(
            width = self._active_handle_width,
            height = self._active_handle_height,
            depth = self._active_handle_width,
            center = Vector(0, self._handle_offset_a, -self._handle_offset_b),
            color = self._extra_widgets_color_map[self.ExtraWidgets.XNegative90.value],
            axis = Vector.Unit_X,
            angle = 90 + self._angle_offset
        )

        mb.addPyramid(
            width = self._active_handle_width,
            height = self._active_handle_height,
            depth = self._active_handle_width,
            center = Vector(self._handle_offset_b, 0, self._handle_offset_a),
            color = self._extra_widgets_color_map[self.ExtraWidgets.YPositive90.value],
            axis = Vector.Unit_Z,
            angle = 90 - self._angle_offset
        )
        mb.addPyramid(
            width = self._active_handle_width,
            height = self._active_handle_height,
            depth = self._active_handle_width,
            center = Vector(-self._handle_offset_b, 0, self._handle_offset_a),
            color = self._extra_widgets_color_map[self.ExtraWidgets.YNegative90.value],
            axis = Vector.Unit_Z,
            angle = -90 + self._angle_offset
        )

        mb.addPyramid(
            width = self._active_handle_width,
            height = self._active_handle_height,
            depth = self._active_handle_width,
            center = Vector(self._handle_offset_a, self._handle_offset_b, 0),
            color = self._extra_widgets_color_map[self.ExtraWidgets.ZPositive90.value],
            axis = Vector.Unit_Z,
            angle = - self._angle_offset
        )
        mb.addPyramid(
            width = self._active_handle_width,
            height = self._active_handle_height,
            depth = self._active_handle_width,
            center = Vector(self._handle_offset_a, -self._handle_offset_b, 0),
            color = self._extra_widgets_color_map[self.ExtraWidgets.ZNegative90.value],
            axis = Vector.Unit_Z,
            angle = 180 + self._angle_offset
        )

        self.setSelectionMesh(mb.build())
