# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import SelectionTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "tool",
        "plugin": {
            "name": "Selection Tool",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Selection Tool plugin description", "Provides the Selection tool.")
        },
        "tool": {
            "visible": False
        }
    }

def register(app):
    return { "tool": SelectionTool.SelectionTool() }
