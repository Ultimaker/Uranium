from UM.Scene.ToolHandle import ToolHandle
from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class VertexEraseToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        lines = MeshData()
        lines.addVertex(0, 0, 0)
        lines.setVertexColor(0, ToolHandle.YAxisColor)

        #self.setPointMesh(lines)
        mb = MeshBuilder()
        mb.addArc(
            radius = 2,
            axis = Vector.Unit_Z,
            color = ToolHandle.YAxisColor
        )
            

        self.setLineMesh(mb.getData())
    
        