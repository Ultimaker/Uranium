from . import ScaleTool

from UM.i18n import i18nc

def getMetaData():
    return {
        'name': 'Scale Tool',
        'displayName': i18nc('Scale tool toolbar button', 'Scale'),
        'type': 'Tool',
        'description': i18nc('Scale tooltip', 'Scale Object'),
        'icon': 'scale.png'
    }

def register(app):
    app.getController().addTool('ScaleTool', ScaleTool.ScaleTool('ScaleTool'))
