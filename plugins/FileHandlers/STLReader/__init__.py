from . import STLReader
def getMetaData():
    return {
        'type': 'mesh_reader',
        'plugin': {
            "name": "STL Reader",
        },
        'mesh_reader': {
            'extension': 'stl',
            'description': 'STL File'
        }
    }

def register(app):
    return STLReader.STLReader()
