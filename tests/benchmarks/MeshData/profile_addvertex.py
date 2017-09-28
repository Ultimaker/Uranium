# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Mesh.MeshData import MeshData

@profile
def addVertex(mesh):
    mesh.addVertex(0, 1, 0)

mesh = MeshData()
mesh.reserveVertexCount(1000000)
for i in range(1000000):
    addVertex(mesh)
