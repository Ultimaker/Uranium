# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import MirrorTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": "Mirror Tool",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Mirror Tool plugin description", "Provides the Mirror tool."),
            "api": 2
        },
        "tool": {
            "name": i18n_catalog.i18nc("Mirror Tool name", "Mirror"),
            "description": i18n_catalog.i18nc("Mirror Tool description", "Mirror Object"),
            "icon": "mirror"
        },
    }

def register(app):
    return { "tool": MirrorTool.MirrorTool() }
