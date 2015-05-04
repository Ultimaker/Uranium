from . import WireframeView

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "view",
        "plugin": {
            "name": "Wireframe View",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("Wireframe View plugin description", "Provides a simple wireframe view")
        },
        "view": {
            "name": i18n_catalog.i18nc("Wireframe View plugin view name", "Wireframe"),
            "visible": False
        }
    }


def register(app):
    return { "view": WireframeView.WireframeView() }
