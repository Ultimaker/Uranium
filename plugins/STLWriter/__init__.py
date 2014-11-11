from STLWriter import STLWriter
def getMetaData():
    return { "name": "STLWriter", "type": "MeshHandler"  }

def register(app):
    app.getMeshFileHandler().addWriter(STLWriter())