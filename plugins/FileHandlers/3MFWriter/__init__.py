# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import ThreeMFWriter

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": catalog.i18nc("@label", "3MF Writer"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": catalog.i18nc("@info:whatsthis", "Provides support for reading 3MF files."),
            "api": 2
        },
        "mesh_writer": {
            "extension": "3mf",
            "description": catalog.i18nc("@item:inlistbox", "3MF File")
        }
    }
def register(app):
    return { "mesh_writer": ThreeMFWriter.ThreeMFWriter() }