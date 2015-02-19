from . import RotateTool

from UM.i18n import i18nc

def getMetaData():
    return {
        'name': 'Rotate Tool',
        'displayName': i18nc('Rotate tool toolbar button name', 'Rotate'),
        'type': 'Tool',
        'description': i18nc('Rotate tool tooltip', 'Rotate Object'),
        'icon': 'rotate.png'
    }

def register(app):
    app.getController().addTool('RotateTool', RotateTool.RotateTool('Rotate'))
