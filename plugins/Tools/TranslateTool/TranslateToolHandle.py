# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class TranslateToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._enabled_axis = [self.XAxis, self.YAxis, self.ZAxis]
        self._lineWidth = 0.5
        self._lineLength= 40
        self._handlePosition = 40
        self._handleHeight = 7
        self._handleWidth = 3

    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self._rebuild()

    def _rebuild(self):
        mb = MeshBuilder()

        #LINES
        if self.YAxis in self._enabled_axis:
            mb.addCube(
                width = self._lineWidth,
                height = self._lineLength,
                depth = self._lineWidth,
                center = Vector(0, self._handlePosition/2, 0),
                color = ToolHandle.YAxisColor
            )
        if self.XAxis in self._enabled_axis:
            mb.addCube(
                width = self._lineLength,
                height = self._lineWidth,
                depth = self._lineWidth,
                center = Vector(self._handlePosition/2, 0, 0),
                color = ToolHandle.XAxisColor
            )

        if self.ZAxis in self._enabled_axis:
            mb.addCube(
                width = self._lineWidth,
                height = self._lineWidth,
                depth = self._lineLength,
                center = Vector(0, 0, self._handlePosition/2),
                color = ToolHandle.ZAxisColor
            )

        #HANDLES
        if self.YAxis in self._enabled_axis:
            mb.addPyramid(
                width = self._handleWidth,
                height = self._handleHeight,
                depth = self._handleWidth,
                center = Vector(0, self._handlePosition, 0),
                color = ToolHandle.YAxisColor
            )

        if self.XAxis in self._enabled_axis:
            mb.addPyramid(
                width = self._handleWidth,
                height = self._handleHeight,
                depth = self._handleWidth,
                center = Vector(self._handlePosition, 0, 0),
                color = ToolHandle.XAxisColor,
                axis = Vector.Unit_Z,
                angle = 90
            )

        if self.ZAxis in self._enabled_axis:
            mb.addPyramid(
                width = self._handleWidth,
                height = self._handleHeight,
                depth = self._handleWidth,
                center = Vector(0, 0, self._handlePosition),
                color = ToolHandle.ZAxisColor,
                axis = Vector.Unit_X,
                angle = -90
            )

        self.setSolidMesh(mb.getData())
