from . import RotateTool

toolName = 'RotateTool'

def getMetaData():
    return {
        'name': toolName,
        'type': 'Tool',
        'description': 'Rotate Object',
        'icon': 'rotate.png'
    }

def register(app):
    app.getController().addTool(toolName, RotateTool.RotateTool(toolName))
