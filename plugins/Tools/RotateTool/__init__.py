# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import RotateTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "Rotate Tool"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Provides the Rotate tool."),
            "api": 3
        },
        "tool": {
            "name": i18n_catalog.i18nc("@label", "Rotate"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Rotate Model"),
            "icon": "rotate",
            "tool_panel": "RotateTool.qml",
            "weight": 1
        }
    }

def register(app):
    return { "tool": RotateTool.RotateTool() }
