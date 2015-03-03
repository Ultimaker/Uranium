from . import SelectionTool

def getMetaData():
    return {
        'type': 'tool',
        'plugin': {
            'name': 'Selection Tool'
        },
        'tool': {
            'visible': False
        }
    }

def register(app):
    return SelectionTool.SelectionTool()
