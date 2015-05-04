#Shoopdawoop
from . import OBJReader

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "type": "mesh_reader",
        "plugin": {
            "name": "Wavefront OBJ Reader",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("OBJ Reader plugin description", "Makes it possbile to read Wavefront OBJ files.")
        },
        "mesh_reader": {
            "extension": "obj",
            "description": i18n_catalog.i18nc("OBJ Reader file format", "Wavefront OBJ File")
        }
    }

def register(app):
    return { "mesh_reader": OBJReader.OBJReader() }
