from . import MeshView


def getMetaData():
    return {
        'type': 'view',
        'plugin': {
            "name": "Mesh View"
        },
        'view': {
            'name': 'Solid'
        }
    }


def register(app):
    return {"view":MeshView.MeshView()}
