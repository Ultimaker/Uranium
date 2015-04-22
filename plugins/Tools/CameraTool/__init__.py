from . import CameraTool

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Camera Tool'
        },
        'tool': {
            'visible': False
        }
    }

def register(app):
    return {"tool":CameraTool.CameraTool()}
