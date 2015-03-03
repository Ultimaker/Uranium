from . import MeshView
def getMetaData():
    return { "name": "MeshView", "type": "View"  }

def register(app):
    return MeshView.MeshView()
