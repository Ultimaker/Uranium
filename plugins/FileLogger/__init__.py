#Shoopdawoop
from . import FileLogger

from Cura.Logger import Logger

def getMetaData():
    return { "name": "Local File Logger", "type": "Logger" }

def register(app):
    Logger.addLogger(FileLogger.FileLogger('cura.log'))
