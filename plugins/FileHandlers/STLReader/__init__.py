from . import STLReader
def getMetaData():
    return { "name": "STLReader", "type": "MeshHandler"  }

def register(app):
    return STLReader.STLReader()
