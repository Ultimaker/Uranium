# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.ToolHandle import ToolHandle
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector

import math

class RotateToolHandle(ToolHandle):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._innerRadius = 40
        self._outerRadius = 40.5
        self._lineWidth = 0.5
        self._activeInnerRadius = 37
        self._activeOuterRadius = 44
        self._activeLineWidth = 3

        #SOLIDMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._innerRadius,
            outer_radius = self._outerRadius,
            width = self._lineWidth,
            color = ToolHandle.ZAxisColor
        )

        mb.addDonut(
            inner_radius = self._innerRadius,
            outer_radius = self._outerRadius,
            width = self._lineWidth,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = ToolHandle.YAxisColor
        )

        mb.addDonut(
            inner_radius = self._innerRadius,
            outer_radius = self._outerRadius,
            width = self._lineWidth,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = ToolHandle.XAxisColor
        )
        self.setSolidMesh(mb.getData())

        #SELECTIONMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._activeInnerRadius,
            outer_radius = self._activeOuterRadius,
            width = self._activeLineWidth,
            color = ToolHandle.ZAxisColor
        )

        mb.addDonut(
            inner_radius = self._activeInnerRadius,
            outer_radius = self._activeOuterRadius,
            width = self._activeLineWidth,
            axis = Vector.Unit_X,
            angle = math.pi / 2,
            color = ToolHandle.YAxisColor
        )

        mb.addDonut(
            inner_radius = self._activeInnerRadius,
            outer_radius = self._activeOuterRadius,
            width = self._activeLineWidth,
            axis = Vector.Unit_Y,
            angle = math.pi / 2,
            color = ToolHandle.XAxisColor
        )

        self.setSelectionMesh(mb.getData())
