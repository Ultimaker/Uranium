# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Mesh.MeshData import MeshData

@profile
def reserveFaceCount(mesh):
    mesh.reserveFaceCount(10000)

@profile
def reserveVertexCount(mesh):
    mesh.reserveVertexCount(30000)

mesh = MeshData()
for i in range(100):
    reserveFaceCount(mesh)

mesh = MeshData()
for i in range(100):
    reserveVertexCount(mesh)
