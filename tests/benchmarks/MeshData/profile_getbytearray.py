from UM.MeshHandling.MeshData import MeshData

@profile
def getByteArray(mesh):
    return mesh.getVerticesAsByteArray()

mesh = MeshData()
mesh.reserveVertexCount(10000)
for i in range(10000):
    mesh.addVertex(0, 1, 0)

for i in range(100):
    a = getByteArray(mesh)
