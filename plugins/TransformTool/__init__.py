from . import TransformTool
def getMetaData():
    return { "name": "TransformTool", "type": "Tool"  }

def register(app):
    app.getController().addTool("TransformTool", TransformTool.TransformTool())
