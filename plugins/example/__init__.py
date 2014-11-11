def getMetaData():
    return { "name": "shoopdawoop" }

def register():
    MeshFileHanlder.get().addMeshLoader( ExampleMeshLoader() )