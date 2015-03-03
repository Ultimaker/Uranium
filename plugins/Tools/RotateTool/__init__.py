from . import RotateTool

from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog('plugins')

def getMetaData():
    return {
        'name': 'Rotate Tool',
        'displayName': i18n_catalog.i18nc('Rotate tool toolbar button name', 'Rotate'),
        'type': 'Tool',
        'description': i18n_catalog.i18nc('Rotate tool tooltip', 'Rotate Object'),
        'icon': 'rotate.png'
    }

def register(app):
    return RotateTool.RotateTool()
