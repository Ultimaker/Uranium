# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import TranslateTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "tool",
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "Translate Tool"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Provides the Translate tool."),
            "api": 3
        },
        "tool": {
            "name": i18n_catalog.i18nc("@action:button", "Move"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Move Model"),
            "icon": "translate",
            "tool_panel": "TranslateTool.qml",
            "weight": -1
        }
    }

def register(app):
    return { "tool": TranslateTool.TranslateTool() }
