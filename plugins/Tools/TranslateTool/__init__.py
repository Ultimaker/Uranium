from . import TranslateTool

def getMetaData():
    return {
        'name': 'Translate Tool',
        'displayName': 'Translate',
        'type': 'Tool',
        'description': 'Translate Object',
        'cura': {
            'visible': False
        }
    }

def register(app):
    app.getController().addTool('TranslateTool', TranslateTool.TranslateTool('Translate'))
