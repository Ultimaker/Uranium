from . import ScaleTool

def getMetaData():
    return {
        'name': 'Scale Tool',
        'displayName': 'Scale',
        'type': 'Tool',
        'description': 'Scale Object',
        'icon': 'scale.png'
    }

def register(app):
    app.getController().addTool('ScaleTool', ScaleTool.ScaleTool('ScaleTool'))
