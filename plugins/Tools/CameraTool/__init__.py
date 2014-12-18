from . import CameraTool

toolName = 'CameraTool'

def getMetaData():
    return {
        'name': toolName,
        'type': 'Tool',
        'visible': False
    }

def register(app):
    app.getController().addTool(toolName, CameraTool.CameraTool(toolName))
