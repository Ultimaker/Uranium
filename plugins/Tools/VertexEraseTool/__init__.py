from . import VertexEraseTool

from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog('plugins')

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Erase Tool'
        },
        'tool': {
            'name': i18n_catalog.i18nc('Erase tool toolbar button', 'Erase'),
            'description': i18n_catalog.i18nc('erase tool description', 'Remove points'),
        },
	'cura': {
	    'tool': {
                'visible': False
	    }
	}
    }

def register(app):
    return VertexEraseTool.VertexEraseTool()
