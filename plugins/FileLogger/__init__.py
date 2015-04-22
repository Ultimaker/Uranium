#Shoopdawoop
from . import FileLogger

from UM.Logger import Logger

def getMetaData():
    return {
        'type': 'logger',
        'plugin': {
            "name": "Local File Logger"
        }
    }

def register(app):
    return {"logger":FileLogger.FileLogger('{0}.log'.format(app.getApplicationName()))}
