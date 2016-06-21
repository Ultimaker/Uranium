# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import UpdateChecker

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "Update Checker"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Checks for updates of the software."),
            "api": 3
        }
    }

def register(app):
    return { "extension": UpdateChecker.UpdateChecker() }
