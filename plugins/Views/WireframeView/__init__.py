from . import WireframeView
def getMetaData():
    return { "name": "WireframeView", "type": "View"  }

def register(app):
    app.getController().addView("WireframeView", WireframeView.WireframeView())
