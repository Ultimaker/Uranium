# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Scene.ToolHandle import ToolHandle


class TranslateToolHandle(ToolHandle):
    """Provides the two block-shaped toolhandles connected with a line for each axis for the translate tool"""

    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = "TranslateToolHandle"
        self._enabled_axis = [self.XAxis, self.YAxis, self.ZAxis]
        self._line_width = 0.5
        self._line_length = 40
        self._handle_position = 40
        self._handle_height = 7
        self._handle_width = 3

        self._active_line_width = 0.8
        self._active_line_length = 40
        self._active_handle_position = 40
        self._active_handle_height = 9
        self._active_handle_width = 7

    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self.buildMesh()

    def buildMesh(self):
        mb = MeshBuilder()

        #SOLIDMESH -> LINES
        if self.YAxis in self._enabled_axis:
            mb.addCube(
                width = self._line_width,
                height = self._line_length,
                depth = self._line_width,
                center = Vector(0, self._handle_position / 2, 0),
                color = self._y_axis_color
            )
        if self.XAxis in self._enabled_axis:
            mb.addCube(
                width = self._line_length,
                height = self._line_width,
                depth = self._line_width,
                center = Vector(self._handle_position / 2, 0, 0),
                color = self._x_axis_color
            )

        if self.ZAxis in self._enabled_axis:
            mb.addCube(
                width = self._line_width,
                height = self._line_width,
                depth = self._line_length,
                center = Vector(0, 0, self._handle_position / 2),
                color = self._z_axis_color
            )

        #SOLIDMESH -> HANDLES
        if self.YAxis in self._enabled_axis:
            mb.addPyramid(
                width = self._handle_width,
                height = self._handle_height,
                depth = self._handle_width,
                center = Vector(0, self._handle_position, 0),
                color = self._y_axis_color
            )

        if self.XAxis in self._enabled_axis:
            mb.addPyramid(
                width = self._handle_width,
                height = self._handle_height,
                depth = self._handle_width,
                center = Vector(self._handle_position, 0, 0),
                color = self._x_axis_color,
                axis = Vector.Unit_Z,
                angle = 90
            )

        if self.ZAxis in self._enabled_axis:
            mb.addPyramid(
                width = self._handle_width,
                height = self._handle_height,
                depth = self._handle_width,
                center = Vector(0, 0, self._handle_position),
                color = self._z_axis_color,
                axis = Vector.Unit_X,
                angle = -90
            )

        self.setSolidMesh(mb.build())

        mb = MeshBuilder()
        #SELECTIONMESH -> LINES
        if self.YAxis in self._enabled_axis:
            mb.addCube(
                width = self._active_line_width,
                height = self._active_line_length,
                depth = self._active_line_width,
                center = Vector(0, self._active_handle_position / 2, 0),
                color = self._y_axis_color
            )
        if self.XAxis in self._enabled_axis:
            mb.addCube(
                width = self._active_line_length,
                height = self._active_line_width,
                depth = self._active_line_width,
                center = Vector(self._active_handle_position / 2, 0, 0),
                color = self._x_axis_color
            )

        if self.ZAxis in self._enabled_axis:
            mb.addCube(
                width = self._active_line_width,
                height = self._active_line_width,
                depth = self._active_line_length,
                center = Vector(0, 0, self._active_handle_position / 2),
                color = self._z_axis_color
            )

        #SELECTIONMESH -> HANDLES
        mb.addCube(
            width = self._active_handle_width,
            height = self._active_handle_width,
            depth = self._active_handle_width,
            center = Vector(0, self._active_handle_position, 0),
            color = ToolHandle.YAxisSelectionColor
        )

        mb.addCube(
            width = self._active_handle_width,
            height = self._active_handle_width,
            depth = self._active_handle_width,
            center = Vector(self._active_handle_position, 0, 0),
            color = ToolHandle.XAxisSelectionColor
        )

        mb.addCube(
            width = self._active_handle_width,
            height = self._active_handle_width,
            depth = self._active_handle_width,
            center = Vector(0, 0, self._active_handle_position),
            color = ToolHandle.ZAxisSelectionColor
        )
        self.setSelectionMesh(mb.build())
