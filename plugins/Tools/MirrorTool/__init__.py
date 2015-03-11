from . import MirrorTool

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Mirror Tool'
        },
        'tool': {
            'name': 'Mirror',
            'description': 'Mirror Object'
        },
    }

def register(app):
    return MirrorTool.MirrorTool()
