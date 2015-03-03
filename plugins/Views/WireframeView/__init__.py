from . import WireframeView
def getMetaData():
    return { "name": "WireframeView", "type": "View"  }

def register(app):
    return WireframeView.WireframeView()
