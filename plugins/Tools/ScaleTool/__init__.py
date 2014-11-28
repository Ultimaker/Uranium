from . import ScaleTool

def getMetaData():
    return { "name": "TransformTool", "type": "Tool"  }

def register(app):
    app.getController().addTool("ScaleTool", ScaleTool.ScaleTool())
