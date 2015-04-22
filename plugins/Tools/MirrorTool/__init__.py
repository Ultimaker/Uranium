from . import MirrorTool

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Mirror Tool'
        },
        'tool': {
            'name': 'Mirror',
            'description': 'Mirror Object',
            'icon': 'mirror'
        },
    }

def register(app):
    return {"tool":MirrorTool.MirrorTool()}
