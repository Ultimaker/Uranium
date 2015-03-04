from . import WireframeView
def getMetaData():
    return {
        'type': 'view',
        'plugin': {
            "name": "Wireframe View"
        },
        'view': {
            'name': 'Wireframe'
        }
    }

def register(app):
    return WireframeView.WireframeView()
