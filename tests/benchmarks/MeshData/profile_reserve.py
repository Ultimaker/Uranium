from UM.MeshHandling.MeshData import MeshData

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
