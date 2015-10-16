# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class MirrorToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._handleWidth = 8
        self._handleHeight = 14
        self._handlePosition = 20

        mb = MeshBuilder()

        mb.addPyramid(
            width = self._handleWidth,
            height = self._handleHeight,
            depth = self._handleWidth,
            center = Vector(0, self._handlePosition, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addPyramid(
            width = self._handleWidth,
            height = self._handleHeight,
            depth = self._handleWidth,
            center = Vector(0, -self._handlePosition, 0),
            color = ToolHandle.YAxisColor,
            axis = Vector.Unit_X,
            angle = 180
        )

        mb.addPyramid(
            width = self._handleWidth,
            height = self._handleHeight,
            depth = self._handleWidth,
            center = Vector(self._handlePosition, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = 90
        )

        mb.addPyramid(
            width = self._handleWidth,
            height = self._handleHeight,
            depth = self._handleWidth,
            center = Vector(-self._handlePosition, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = -90
        )

        mb.addPyramid(
            width = self._handleWidth,
            height = self._handleHeight,
            depth = self._handleWidth,
            center = Vector(0, 0, -self._handlePosition),
            color = ToolHandle.ZAxisColor,
            axis = Vector.Unit_X,
            angle = 90
        )

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
        self.setSelectionMesh(mb.getData())
