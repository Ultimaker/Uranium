# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import MirrorTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "tool": {
            "name": i18n_catalog.i18nc("@label", "Mirror"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Mirror Model"),
            "icon": "mirror",
            "weight": 2
        },
    }

def register(app):
    return { "tool": MirrorTool.MirrorTool() }
