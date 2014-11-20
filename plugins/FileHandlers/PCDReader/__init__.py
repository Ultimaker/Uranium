#Shoopdawoop
from . import PCDReader
def getMetaData():
    return { "name": "PCDReader", "type": "MeshHandler"  }

def register(app):
    app.getMeshFileHandler().addReader(PCDReader.PCDReader())
