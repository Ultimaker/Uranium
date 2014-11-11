from STLReader import STLReader
def getMetaData():
    return { "name": "STLReader", "type": "MeshHandler"  }

def register(app):
    app.getMeshFileHandler().addReader(STLReader())