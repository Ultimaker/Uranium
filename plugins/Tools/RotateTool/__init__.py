from . import RotateTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "tool",
        "plugin": {
            "name": "Rotate Tool",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Rotate Tool plugin description", "Provides the Rotate tool.")
        },
        "tool": {
            "name": i18n_catalog.i18nc("Rotate tool name", "Rotate"),
            "description": i18n_catalog.i18nc("Rotate tool description", "Rotate Object"),
            "icon": "rotate",
            "tool_panel": "RotateTool.qml"
        }
    }

def register(app):
    return { "tool": RotateTool.RotateTool() }
