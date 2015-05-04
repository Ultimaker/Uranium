#Shoopdawoop
from . import MLPReader

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "workspace_reader",
        "plugin": {
            "name": "MeshLab Project Reader",
            "author": "Ultimaker" ,
            "description": "Save workspace to a MeshLab project file",
            "version":"1.0"
        }
    }

def register(app):
    return {"workspace_reader":MLPReader.MLPReader()}
