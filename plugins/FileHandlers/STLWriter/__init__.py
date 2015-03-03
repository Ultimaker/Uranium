from . import STLWriter
def getMetaData():
    return { "name": "STLWriter", "type": "MeshHandler"  }

def register(app):
    return STLWriter.STLWriter()
