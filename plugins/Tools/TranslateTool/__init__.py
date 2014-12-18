from . import TranslateTool

toolName = 'TranslateTool'

def getMetaData():
    return {
        'name': toolName,
        'type': 'Tool',
        'description': 'Translate Object',
        'printer': {
            'visible': False
        }
    }

def register(app):
    app.getController().addTool(toolName, TranslateTool.TranslateTool(toolName))
