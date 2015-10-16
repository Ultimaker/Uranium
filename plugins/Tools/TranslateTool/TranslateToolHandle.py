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

        self._activeLineWidth = 0.8
        self._activeLineLength= 40
        self._activeHandlePosition = 40
        self._activeHandleHeight = 9
        self._activeHandleWidth = 7

    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self._rebuild()

    def _rebuild(self):
        mb = MeshBuilder()

        #SOLIDMESH -> LINES
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

        #SOLIDMESH -> HANDLES
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

        mb = MeshBuilder()
        #ACTIVEMESH -> LINES
        if self.YAxis in self._enabled_axis:
            mb.addCube(
                width = self._activeLineWidth,
                height = self._activeLineLength,
                depth = self._activeLineWidth,
                center = Vector(0, self._activeHandlePosition/2, 0),
                color = ToolHandle.YAxisColor
            )
        if self.XAxis in self._enabled_axis:
            mb.addCube(
                width = self._activeLineLength,
                height = self._activeLineWidth,
                depth = self._activeLineWidth,
                center = Vector(self._activeHandlePosition/2, 0, 0),
                color = ToolHandle.XAxisColor
            )

        if self.ZAxis in self._enabled_axis:
            mb.addCube(
                width = self._activeLineWidth,
                height = self._activeLineWidth,
                depth = self._activeLineLength,
                center = Vector(0, 0, self._activeHandlePosition/2),
                color = ToolHandle.ZAxisColor
            )

        #SELECTIONMESH -> HANDLES
        mb.addCube(
            width = self._activeHandleWidth,
            height = self._activeHandleWidth,
            depth = self._activeHandleWidth,
            center = Vector(0, 0, 0),
            color = ToolHandle.AllAxisColor
        )

        mb.addCube(
            width = self._activeHandleWidth,
            height = self._activeHandleWidth,
            depth = self._activeHandleWidth,
            center = Vector(0, self._activeHandlePosition, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addCube(
            width = self._activeHandleWidth,
            height = self._activeHandleWidth,
            depth = self._activeHandleWidth,
            center = Vector(self._activeHandlePosition, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addCube(
            width = self._activeHandleWidth,
            height = self._activeHandleWidth,
            depth = self._activeHandleWidth,
            center = Vector(0, 0, self._activeHandlePosition),
            color = ToolHandle.ZAxisColor
        )
        self.setSelectionMesh(mb.getData())
