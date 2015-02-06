from . import SelectionTool

def getMetaData():
    return {
        'name': 'Selection Tool',
        'type': 'Tool',
        'visible': False
    }

def register(app):
    app.getController().addTool('SelectionTool', SelectionTool.SelectionTool('Selection'))
