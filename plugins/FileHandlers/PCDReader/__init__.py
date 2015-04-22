#Shoopdawoop
from . import PCDReader

def getMetaData():
    return {
        'type': 'mesh_reader',
        'plugin': {
            "name": "PCD Reader"
        }
    }

def register(app):
    return {"mesh_reader":PCDReader.PCDReader()}
