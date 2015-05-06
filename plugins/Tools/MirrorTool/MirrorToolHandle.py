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

        mb = MeshBuilder()

        mb.addPyramid(
            width = 4,
            height = 7,
            depth = 4,
            center = Vector(0, 10, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addPyramid(
            width = 4,
            height = 7,
            depth = 4,
            center = Vector(0, -10, 0),
            color = ToolHandle.YAxisColor,
            axis = Vector.Unit_X,
            angle = 180
        )

        mb.addPyramid(
            width = 4,
            height = 7,
            depth = 4,
            center = Vector(10, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = 90
        )

        mb.addPyramid(
            width = 4,
            height = 7,
            depth = 4,
            center = Vector(-10, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = -90
        )

        mb.addPyramid(
            width = 4,
            height = 7,
            depth = 4,
            center = Vector(0, 0, -10),
            color = ToolHandle.ZAxisColor,
            axis = Vector.Unit_X,
            angle = 90
        )

        mb.addPyramid(
            width = 4,
            height = 7,
            depth = 4,
            center = Vector(0, 0, 10),
            color = ToolHandle.ZAxisColor,
            axis = Vector.Unit_X,
            angle = -90
        )

        self.setSolidMesh(mb.getData())
        self.setSelectionMesh(mb.getData())
