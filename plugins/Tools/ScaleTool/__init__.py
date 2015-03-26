from . import ScaleTool

from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog('plugins')

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Scale Tool'
        },
        'tool': {
            'name': i18n_catalog.i18nc('Scale tool toolbar button', 'Scale'),
            'description': i18n_catalog.i18nc('Scale tool description', 'Scale Object'),
            'icon': 'scale'
        }
    }

def register(app):
    return ScaleTool.ScaleTool()
