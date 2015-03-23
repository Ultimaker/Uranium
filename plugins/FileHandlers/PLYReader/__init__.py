#Shoopdawoop
from . import PLYReader
def getMetaData():
    return {
        'type': 'mesh_reader',
        'plugin': {
            "name": "PLY Reader",
        },
        'mesh_reader': {
            'extension': 'ply',
            'description': 'PLY File'
        }
    }

def register(app):
    return PLYReader.PLYReader()
