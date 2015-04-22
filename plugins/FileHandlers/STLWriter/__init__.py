from . import STLWriter
def getMetaData():
    return {
        'type': 'mesh_writer',
        'plugin': {
            "name": "STL Writer"
        },
        'mesh_writer': {
            'extension': 'stl',
            'description': 'STL File'
        }
    }

def register(app):
    return {"mesh_writer":STLWriter.STLWriter()}
