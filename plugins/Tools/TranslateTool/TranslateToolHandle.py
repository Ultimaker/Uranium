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

        mb.addPyramid(
            width = 2,
            height = 4,
            depth = 2,
            center = Vector(0, 20, 0),
            color = ToolHandle.YAxisColor
        )

        mb.addPyramid(
            width = 2,
            height = 4,
            depth = 2,
            center = Vector(20, 0, 0),
            color = ToolHandle.XAxisColor,
            axis = Vector.Unit_Z,
            angle = 90
        )

        mb.addPyramid(
            width = 2,
            height = 4,
            depth = 2,
            center = Vector(0, 0, 20),
            color = ToolHandle.ZAxisColor,
            axis = Vector.Unit_X,
            angle = -90
        )

        self.setSolidMesh(mb.getData())
