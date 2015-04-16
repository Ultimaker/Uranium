from UM.Scene.ToolHandle import ToolHandle
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

import math

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

        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = 18,
            outer_radius = 22,
            width = 2,
            color = ToolHandle.ZAxisColor
        )

        mb.addDonut(
            inner_radius = 18,
            outer_radius = 22,
            width = 2,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = ToolHandle.YAxisColor
        )

        mb.addDonut(
            inner_radius = 18,
            outer_radius = 22,
            width = 2,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = ToolHandle.XAxisColor
        )

        self.setSelectionMesh(mb.getData())
