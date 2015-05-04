from . import UpdateChecker

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "extension",
        "plugin": {
            "name": "Update Checker",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Update Checker plugin description", "Checks for updates of the software.")
        }
    }

def register(app):
    return { "extension": UpdateChecker.UpdateChecker() }
