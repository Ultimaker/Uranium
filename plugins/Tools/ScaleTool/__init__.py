# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import ScaleTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "tool",
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "Scale Tool"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Provides the Scale tool."),
            "api": 3
        },
        "tool": {
            "name": i18n_catalog.i18nc("@label", "Scale"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Scale Model"),
            "icon": "scale",
            "tool_panel": "ScaleTool.qml",
            "weight": 0
        }
    }

def register(app):
    return { "tool": ScaleTool.ScaleTool() }
