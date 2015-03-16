from UM.Scene.ToolHandle import ToolHandle
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

class RotateToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)

        mb = MeshBuilder()

        mb.addArc(
            radius = 20,
            axis = Vector.Unit_X,
            color = ToolHandle.XAxisColor
        )

        mb.addArc(
            radius = 20,
            axis = Vector.Unit_Y,
            color = ToolHandle.YAxisColor
        )

        mb.addArc(
            radius = 20,
            axis = Vector.Unit_Z,
            color = ToolHandle.ZAxisColor
        )

        self.setLineMesh(mb.getData())
