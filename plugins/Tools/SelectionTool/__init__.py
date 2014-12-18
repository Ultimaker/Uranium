from . import SelectionTool

toolName = 'SelectionTool'

def getMetaData():
    return {
        'name': toolName,
        'type': 'Tool',
        'visible': False
    }

def register(app):
    app.getController().addTool(toolName, SelectionTool.SelectionTool(toolName))
