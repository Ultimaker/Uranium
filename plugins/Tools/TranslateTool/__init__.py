from . import TranslateTool

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Translate Tool'
        },
        'tool': {
            'name': 'Translate',
            'description': 'Translate Object'
        },
        'cura': {
            'tool': {
                'visible': False
            }
        }
    }

def register(app):
    return {"tool":TranslateTool.TranslateTool()}
