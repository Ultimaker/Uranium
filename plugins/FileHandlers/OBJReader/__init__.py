#Shoopdawoop
from . import OBJReader

def getMetaData():
    return {
        'type': 'mesh_reader',
        'plugin': {
            "name": "OBJ Reader",
        },
        'mesh_reader': {
            'extension': 'obj',
            'description': 'Wavefront OBJ File'
        }
    }

def register(app):
    return OBJReader.OBJReader()
