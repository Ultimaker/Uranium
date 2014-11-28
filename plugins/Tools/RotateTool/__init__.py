from . import RotateTool

def getMetaData():
    return { "name": "RotateTool", "type": "Tool"  }

def register(app):
    app.getController().addTool("RotateTool", RotateTool.RotateTool())
