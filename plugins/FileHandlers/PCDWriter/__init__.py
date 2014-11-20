#Shoopdawoop
from . import PCDWriter
def getMetaData():
    return { "name": "PCDWriter", "type": "MeshHandler"  }

def register(app):
    app.getMeshFileHandler().addWriter(PCDWriter.PCDWriter())
