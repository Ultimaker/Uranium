#Shoopdawoop
from . import ConsoleLogger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "logger",
        "plugin": {
            "name": "Console Logger",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Console Logger plugin description", "Outputs log information to the console.")
        }
    }

def register(app):
    return { "logger": ConsoleLogger.ConsoleLogger() }
