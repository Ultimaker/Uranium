from MeshView import MeshView
def getMetaData():
    return { "name": "MeshView", "type": "View"  }

def register(app):
    app.getController().addView("MeshView", MeshView())