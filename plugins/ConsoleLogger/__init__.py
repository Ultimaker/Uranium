# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

#Shoopdawoop
from . import ConsoleLogger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "plugin": {
            "name": "Console Logger",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Console Logger plugin description", "Outputs log information to the console."),
            "api": 2
        }
    }

def register(app):
    return { "logger": ConsoleLogger.ConsoleLogger() }
