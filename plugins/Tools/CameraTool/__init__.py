# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import CameraTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "Camera Tool"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Provides the tool to manipulate the camera."),
            "api": 3
        },
        "tool": {
            "visible": False
        }
    }

def register(app):
    return { "tool": CameraTool.CameraTool() }
