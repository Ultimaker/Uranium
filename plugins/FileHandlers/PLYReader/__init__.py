#Shoopdawoop
from . import PLYReader
def getMetaData():
    return {
        'type': 'mesh_reader',
        'plugin': {
            "name": "PLY Reader"
        }
    }

def register(app):
    return PLYReader.PLYReader()
