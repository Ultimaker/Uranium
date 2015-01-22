#Shoopdawoop
from . import MLPWriter
def getMetaData():
    return {"name": "MLPWriter", 
            "type": "WorkspaceHandler", 
            "author": "Jaime van Kessel & Arjen Hiemstra" ,
            "about":"Load workspace from meshlab project file",
            "version":"1.0" }

def register(app):
    app.getWorkspaceFileHandler().addWriter(MLPWriter.MLPWriter())