# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

#Shoopdawoop
from . import OBJReader

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "mesh_reader": [
            {
                "extension": "obj",
                "description": i18n_catalog.i18nc("@item:inlistbox", "Wavefront OBJ File")
            }
        ]
    }


def register(app):
    return {"mesh_reader": OBJReader.OBJReader()}
