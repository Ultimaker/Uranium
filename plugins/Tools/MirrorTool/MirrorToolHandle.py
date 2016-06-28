# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

##  Provides the two pyramid-shaped toolhandles for each axis for the mirror tool

class MirrorToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._handle_width = 8
        self._handle_height = 14
        self._handle_position = 20

        mb = MeshBuilder()

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(0, self._handle_position, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(0, -self._handle_position, 0),
            color = ToolHandle.YAxisColor,
            axis = Vector.Unit_X,
            angle = 180
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(self._handle_position, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = 90
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(-self._handle_position, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = -90
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(0, 0, -self._handle_position),
            color = ToolHandle.ZAxisColor,
            axis = Vector.Unit_X,
            angle = 90
        )

        mb.addPyramid(
            width = self._handle_width,
            height = self._handle_height,
            depth = self._handle_width,
            center = Vector(0, 0, self._handle_position),
            color = ToolHandle.ZAxisColor,
            axis = Vector.Unit_X,
            angle = -90
        )
        mesh = mb.build()
        self.setSolidMesh(mesh)
        self.setSelectionMesh(mesh)
