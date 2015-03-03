#Shoopdawoop
from . import OBJReader
def getMetaData():
    return { "name": "OBJReader", "type": "MeshHandler"  }

def register(app):
    return OBJReader.OBJReader()
