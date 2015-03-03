#Shoopdawoop
from . import ConsoleLogger

from UM.Logger import Logger

def getMetaData():
    return { "name": "Console Logger", "type": "Logger" }

def register(app):
    return ConsoleLogger.ConsoleLogger()
