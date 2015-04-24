from . import VertexSelectionTool


def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'vertex selection Tool'
        },
        'tool': {
            'visible': False
        }
    }

def register(app):
    return {"tool": VertexSelectionTool.VertexSelectionTool()}
