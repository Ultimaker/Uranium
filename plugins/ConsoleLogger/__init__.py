#Shoopdawoop
from . import ConsoleLogger

from Cura.Logger import Logger

def getMetaData():
    return { "name": "Console Logger", "type": "Logger" }

def register(app):
    Logger.addLogger(ConsoleLogger.ConsoleLogger())
