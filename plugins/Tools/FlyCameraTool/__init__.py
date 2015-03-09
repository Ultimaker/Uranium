from . import FlyCameraTool
def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Fly Camera Tool'
        },
        'tool': {
            'visible': False
        }
    }

def register(app):
    return FlyCameraTool.FlyCameraTool()