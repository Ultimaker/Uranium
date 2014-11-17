from . import TransformTool
def getMetaData():
    return { "name": "TransformTool", "type": "tool"  }

def register(app):
    app.getController().addTool("TransformTool", TransformTool.TransformTool())
