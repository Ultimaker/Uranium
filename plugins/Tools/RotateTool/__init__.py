from . import RotateTool

def getMetaData():
    return {
        'name': 'Rotate Tool',
        'displayName': 'Rotate',
        'type': 'Tool',
        'description': 'Rotate Object',
        'icon': 'rotate.png'
    }

def register(app):
    app.getController().addTool('RotateTool', RotateTool.RotateTool('Rotate'))
