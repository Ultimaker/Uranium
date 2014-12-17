from . import TranslateTool

toolName = 'TranslateTool'

def getMetaData():
    return { "name": toolName, "type": "Tool" }

def register(app):
    app.getController().addTool(toolName, TranslateTool.TranslateTool())
