from . import OBJWriter
def getMetaData():
    return { "name": "OBJWriter", "type": "MeshHandler"  }

def register(app):
    app.getMeshFileHandler().addWriter(OBJWriter.OBJWriter())