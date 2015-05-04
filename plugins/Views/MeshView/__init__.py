from . import MeshView

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "view",
        "plugin": {
            "name": "Mesh View",
            "author": "Ultimaker",
            "version": "1.0",
            "decription": i18n_catalog.i18nc("Mesh View plugin description", "Provides a normal solid mesh view.")
        },
        "view": {
            "name": i18n_catalog.i18nc("Mesh View plugin view name", "Solid")
        }
    }

def register(app):
    return { "view": MeshView.MeshView() }
