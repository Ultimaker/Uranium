#Shoopdawoop
from . import FileLogger

from UM.Logger import Logger

def getMetaData():
    return { "name": "Local File Logger", "type": "Logger" }

def register(app):
    Logger.addLogger(FileLogger.FileLogger('UM.log'))
