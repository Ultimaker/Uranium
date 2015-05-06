# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

#Shoopdawoop
from . import MLPWriter



def getMetaData():
    return {
        "type": "workspace_writer",
        "plugin": {
            "name": "MLPWriter",
            "author": "Jaime van Kessel & Arjen Hiemstra" ,
            "description":"Load workspace from meshlab project file",
            "version":"1.0"
        }
    }

def register(app):
    return {"workspace_writer":MLPWriter.MLPWriter()}
