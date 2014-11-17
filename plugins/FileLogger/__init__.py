#Shoopdawoop
from . import FileLogger

def getMetaData():
    return { "name": "Local File Logger", "type": "Logger" }

def register(app):
    app.addLogger(FileLogger.FileLogger('cura.log'))
