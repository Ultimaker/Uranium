from . import WireframeView


def getMetaData():
    return {
        'type': 'view',
        'plugin': {
            "name": "Wireframe View"
        },
        'view': {
            'name': 'Wireframe',
            'visible': False
        }
    }


def register(app):
    return {"view": WireframeView.WireframeView()}
