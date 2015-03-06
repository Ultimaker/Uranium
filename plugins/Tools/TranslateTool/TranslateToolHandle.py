from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class TranslateToolHandle(ToolHandle):
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

        # Y Axis
        mb.addFace(
            Vector(-1, 20, 1),
            Vector(1, 20, 1),
            Vector(0, 24, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addFace(
            Vector(1, 20, 1),
            Vector(1, 20, -1),
            Vector(0, 24, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addFace(
            Vector(1, 20, -1),
            Vector(-1, 20, -1),
            Vector(0, 24, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addFace(
            Vector(-1, 20, -1),
            Vector(-1, 20, 1),
            Vector(0, 24, 0),
            color = ToolHandle.YAxisColor
        )

        # X Axis
        mb.addFace(
            Vector(20, -1, 1),
            Vector(20, 1, 1),
            Vector(24, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addFace(
            Vector(20, 1, 1),
            Vector(20, 1, -1),
            Vector(24, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addFace(
            Vector(20, 1, -1),
            Vector(20, -1, -1),
            Vector(24, 0, 0),
            color = ToolHandle.XAxisColor
        )

        mb.addFace(
            Vector(20, -1, -1),
            Vector(20, -1, 1),
            Vector(24, 0, 0),
            color = ToolHandle.XAxisColor
        )

        # Z Axis
        mb.addFace(
            Vector(-1, 1, 20),
            Vector(1, 1, 20),
            Vector(0, 0, 24),
            color = ToolHandle.ZAxisColor
        )

        mb.addFace(
            Vector(1, 1, 20),
            Vector(1, -1, 20),
            Vector(0, 0, 24),
            color = ToolHandle.ZAxisColor
        )

        mb.addFace(
            Vector(1, -1, 20),
            Vector(-1, -1, 20),
            Vector(0, 0, 24),
            color = ToolHandle.ZAxisColor
        )

        mb.addFace(
            Vector(-1, -1, 20),
            Vector(-1, 1, 20),
            Vector(0, 0, 24),
            color = ToolHandle.ZAxisColor
        )

        self.setSolidMesh(mb.getData())
