#Shoopdawoop
from . import MLPReader
def getMetaData():
    return {"name": "MLPReader", 
            "type": "WorkspaceHandler", 
            "author": "Jaime van Kessel & Arjen Hiemstra" ,
            "about":"Save workspace to meshlab project file",
            "version":"1.0" }

def register(app):
    return MLPReader.MLPReader()
