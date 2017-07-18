# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import STLWriter

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "mesh_writer": {
            "output": [
                {
                    "mime_type": "application/x-stl-ascii",
                    "mode": STLWriter.STLWriter.OutputMode.TextMode,
                    "extension": "stl",
                    "description": i18n_catalog.i18nc("@item:inlistbox", "STL File (ASCII)")
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
