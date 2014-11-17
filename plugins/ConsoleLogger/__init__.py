#Shoopdawoop
from . import ConsoleLogger

def getMetaData():
    return { "name": "Console Logger", "type": "Logger" }

def register(app):
    app.addLogger(ConsoleLogger.ConsoleLogger())