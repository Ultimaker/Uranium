from . import CameraTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "tool",
        "plugin": {
            "name": "Camera Tool",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Camera Tool plugin description", "Provides the tool to manipulate the camera.")
        },
        "tool": {
            "visible": False
        }
    }

def register(app):
    return { "tool": CameraTool.CameraTool() }
