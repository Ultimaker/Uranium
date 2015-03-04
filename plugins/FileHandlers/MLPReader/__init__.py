#Shoopdawoop
from . import MLPReader

def getMetaData():
    return {
        'type': 'workspace_reader',
        'plugin': {
            'name': "MLPReader",
            "author": "Jaime van Kessel & Arjen Hiemstra" ,
            "description": "Save workspace to meshlab project file",
            "version":"1.0"
        }
    }

def register(app):
    return MLPReader.MLPReader()
