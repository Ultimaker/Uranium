# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class ScaleToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        lines = MeshData()
        lines.addVertex(0, 0, 0)
        lines.addVertex(0, 20, 0)
        lines.addVertex(0, 0, 0)
        lines.addVertex(20, 0, 0)
        lines.addVertex(0, 0, 0)
        lines.addVertex(0, 0, 20)

        lines.setVertexColor(0, ToolHandle.YAxisColor)
        lines.setVertexColor(1, ToolHandle.YAxisColor)
        lines.setVertexColor(2, ToolHandle.XAxisColor)
        lines.setVertexColor(3, ToolHandle.XAxisColor)
        lines.setVertexColor(4, ToolHandle.ZAxisColor)
        lines.setVertexColor(5, ToolHandle.ZAxisColor)

        self.setLineMesh(lines)

        mb = MeshBuilder()

        mb.addCube(
            width = 2,
            height = 2,
            depth = 2,
            center = Vector(0, 0, 0),
            color = ToolHandle.AllAxisColor
        )

        mb.addCube(
            width = 2,
            height = 2,
            depth = 2,
            center = Vector(0, 20, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addCube(
            width = 2,
            height = 2,
            depth = 2,
            center = Vector(20, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addCube(
            width = 2,
            height = 2,
            depth = 2,
            center = Vector(0, 0, 20),
            color = ToolHandle.ZAxisColor
        )

        self.setSolidMesh(mb.getData())

        mb = MeshBuilder()

        mb.addCube(
            width = 2,
            height = 22,
            depth = 2,
            center = Vector(0, 11, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addCube(
            width = 22,
            height = 2,
            depth = 2,
            center = Vector(11, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addCube(
            width = 2,
            height = 2,
            depth = 22,
            center = Vector(0, 0, 11),
            color = ToolHandle.ZAxisColor
        )

        mb.addCube(
            width = 4,
            height = 4,
            depth = 4,
            center = Vector(0, 0, 0),
            color = ToolHandle.AllAxisColor
        )

        self.setSelectionMesh(mb.getData())
