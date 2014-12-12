from Cura.MeshHandling.MeshData import MeshData

@profile
def addVertex(mesh):
    mesh.addVertex(0, 1, 0)

mesh = MeshData()
mesh.reserveVertexCount(1000000)
for i in range(1000000):
    addVertex(mesh)
