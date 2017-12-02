# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import TranslateTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
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
