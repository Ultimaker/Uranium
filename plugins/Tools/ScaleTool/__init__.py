from . import ScaleTool

toolName = 'ScaleTool'

def getMetaData():
    return {
        'name': toolName,
        'type': 'Tool',
        'description': 'Scale Object',
        'icon': 'scale.png'
    }

def register(app):
    app.getController().addTool(toolName, ScaleTool.ScaleTool(toolName))
