from . import PLYWriter

#TODO: We can't quite finish this as we have no real faces to save yet. This writer should work, but is not tested.
def getMetaData():
    return {
        'type': 'mesh_writer',
        'plugin': {
            "name": "PLY Writer",
        },
        'mesh_reader': {
            'extension': 'ply',
            'description': 'PLY File'
        }
    }

def register(app):
    return {"mesh_writer":PLYWriter.PLYWriter()}
