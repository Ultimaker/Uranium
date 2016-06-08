# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import WireframeView

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "view",
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "Wireframe View"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Provides a simple wireframe view."),
            "api": 3
        },
        "view": {
            "name": "Wireframe",
            "visible": False
        }
    }


def register(app):
    return { "view": WireframeView.WireframeView() }
