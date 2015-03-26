from . import RotateTool

from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog('plugins')

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Rotate Tool',
        },
        'tool': {
            'name': i18n_catalog.i18nc('Rotate tool toolbar button name', 'Rotate'),
            'description': i18n_catalog.i18nc('Rotate tool description', 'Rotate Object'),
            'icon': 'rotate'
        }
    }

def register(app):
    return RotateTool.RotateTool()
