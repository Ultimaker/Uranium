# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import STLWriter

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "mesh_writer",
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "STL Writer"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Provides support for writing STL files."),
            "api": 3
        },
        "mesh_writer": {
            "output": [
                {
                    "mime_type": "application/x-stl-ascii",
                    "mode": STLWriter.STLWriter.OutputMode.TextMode,
                    "extension": "stl",
                    "description": i18n_catalog.i18nc("@item:inlistbox", "STL File (Ascii)")
                },
                {
                    "mime_type": "application/x-stl-binary",
                    "mode": STLWriter.STLWriter.OutputMode.BinaryMode,
                    "extension": "stl",
                    "description": i18n_catalog.i18nc("@item:inlistbox", "STL File (Binary)")
                }
            ]
        }
    }

def register(app):
    return { "mesh_writer": STLWriter.STLWriter() }
