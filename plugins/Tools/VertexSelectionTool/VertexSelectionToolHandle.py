from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class VertexSelectionToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        lines = MeshData()
        lines.addVertex(0, 0, 0)
        lines.setVertexColor(0, ToolHandle.YAxisColor)

        #self.setPointMesh(lines)
        mb = MeshBuilder()
        mb.addCube(
            width = 1,
            height = 1,
            depth = 1,
            center = Vector(0, 0, 0),
            color = ToolHandle.XAxisColor
        )
      

        self.setSolidMesh(mb.getData())
    
        