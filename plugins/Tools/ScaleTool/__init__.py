from . import ScaleTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "tool",
        "plugin": {
            "name": "Scale Tool",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Scale Tool plugin description", "Provides the Scale tool.")
        },
        "tool": {
            "name": i18n_catalog.i18nc("Scale Tool name", "Scale"),
            "description": i18n_catalog.i18nc("Scale Tool description", "Scale Object"),
            "icon": "scale",
            "tool_panel": "ScaleTool.qml"
        }
    }

def register(app):
    return { "tool": ScaleTool.ScaleTool() }
