# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import SimpleView

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "view": {
            "name": i18n_catalog.i18nc("@item:inmenu", "Simple"),
            "visible": False
        }
    }

def register(app):
    return { "view": SimpleView.SimpleView() }

