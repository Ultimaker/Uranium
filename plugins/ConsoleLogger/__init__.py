#Shoopdawoop
from . import ConsoleLogger

def getMetaData():
    return {
        'type': 'logger',
        'plugin': {
            "name": "Console Logger"
        }
    }

def register(app):
    return {"logger":ConsoleLogger.ConsoleLogger()}
