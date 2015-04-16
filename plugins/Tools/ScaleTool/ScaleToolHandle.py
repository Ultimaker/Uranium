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
            width = 4,
            height = 20,
            depth = 4,
            center = Vector(0, 10, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addCube(
            width = 4,
            height = 4,
            depth = 4,
            center = Vector(0, 20, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addCube(
            width = 20,
            height = 4,
            depth = 4,
            center = Vector(10, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addCube(
            width = 4,
            height = 4,
            depth = 4,
            center = Vector(20, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addCube(
            width = 4,
            height = 4,
            depth = 20,
            center = Vector(0, 0, 10),
            color = ToolHandle.ZAxisColor
        )

        mb.addCube(
            width = 4,
            height = 4,
            depth = 4,
            center = Vector(0, 0, 20),
            color = ToolHandle.ZAxisColor
        )

        mb.addCube(
            width = 8,
            height = 8,
            depth = 8,
            center = Vector(0, 0, 0),
            color = ToolHandle.AllAxisColor
        )

        self.setSelectionMesh(mb.getData())
