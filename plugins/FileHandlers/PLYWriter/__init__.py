from . import PLYWriter

#TODO: We can't quite finish this as we have no real faces to save yet. This writer should work, but is not tested.
def getMetaData():
    return { "name": "PLYWriter", "type": "MeshHandler"  }

def register(app):
    return PLYWriter.PLYWriter()
