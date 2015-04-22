#Shoopdawoop
from . import PCDWriter
def getMetaData():
    return {
        'type': 'mesh_writer',
        'plugin': {
            "name": "PCDWriter"
        }
    }

def register(app):
    return {"mesh_writer":PCDWriter.PCDWriter()}
