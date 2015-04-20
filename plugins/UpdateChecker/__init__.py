from . import UpdateChecker
from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog('plugins')

def getMetaData():
    return {
        'type': 'extension',
        'plugin': {
            'name': 'Update checker',
            'author': 'Jaime van Kessel',
            'version': '1.0',
            'description': i18n_catalog.i18nc('Version checker description','Check if there are updates of the software. ')
        }
    }
        
def register(app):
    return UpdateChecker.UpdateChecker()