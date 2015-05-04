from . import STLReader

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "mesh_reader",
        "plugin": {
            "name": "STL Reader",
            "author": "Ultimaker",
            "version": "1.0",
            "decription": i18n_catalog.i18nc("STL Reader plugin description", "Provides support for reading STL files.")
        },
        "mesh_reader": {
            "extension": "stl",
            "description": i18n_catalog.i18nc("STL Reader plugin file type", "STL File")
        }
    }

def register(app):
    return { "mesh_reader": STLReader.STLReader() }
