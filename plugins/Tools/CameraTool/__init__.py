from . import CameraTool

toolName = 'CameraTool'

def getMetaData():
    return {
        'name': toolName,
        'type': 'Tool',
        'visible': False
    }

def register(app):
    return CameraTool.CameraTool()
