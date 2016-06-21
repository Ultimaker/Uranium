# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

#Shoopdawoop
from . import FileLogger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": i18n_catalog.i18nc("@label", "File Logger"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("@info:whatsthis", "Outputs log information to the console."),
            "api": 3
        }
    }

def register(app):
    return { "logger": FileLogger.FileLogger("{0}.log".format(app.getApplicationName())) }
