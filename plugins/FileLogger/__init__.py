#Shoopdawoop
from . import FileLogger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "logger",
        "plugin": {
            "name": i18n_catalog.i18nc("File Logger plugin name", "File Logger"),
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Console Logger plugin description", "Outputs log information to the console.")
        }
    }

def register(app):
    return { "logger": FileLogger.FileLogger('{0}.log'.format(app.getApplicationName())) }
