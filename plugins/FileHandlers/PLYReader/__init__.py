#Shoopdawoop
from . import PLYReader
def getMetaData():
    return { "name": "PLYReader", "type": "MeshHandler"  }

def register(app):
    return PLYReader.PLYReader()
