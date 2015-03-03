from . import STLWriter
def getMetaData():
    return {
        'type': 'mesh_writer',
        'plugin': {
            "name": "STL Writer"
        }
    }

def register(app):
    return STLWriter.STLWriter()
