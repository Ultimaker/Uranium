# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject


class Logger:
    ##  Add a logger to the list.
    #   \param logger \type{Logger}
    @classmethod
    def addLogger(cls, logger):
        cls.__loggers.append(logger)

    ##  Get all loggers
    #   \returns \type{list} List of Loggers
    @classmethod
    def getLoggers(cls):
        return cls.__loggers

    ##  Send a message of certain type to all loggers to be handled.
    #   \param log_type \type{string} Values must be; 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning).
    #   \param message \type{string} containing message to be logged
    #   \param message \type{list} List of variables to be added to the message.
    @classmethod
    def log(cls, log_type, message, *args):
        for logger in cls.__loggers:
            filled_message = message % args # Replace all the %s with the variables. Python formating is magic.
            logger.log(log_type, filled_message)

    __loggers = []

##  Abstract base class for log output classes.
class LogOutput(PluginObject):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritence work.
        self._name = type(self).__name__ # Set name of the logger to it's class name
    
    ##  Log a message.
    #
    #   The possible message types are:
    #   - 'd', debug
    #   - 'i', info
    #   - 'w', warning
    #   - 'e', error
    #   - 'c', critical
    #
    #   \param log_type \type{string} A value describing the type of message.
    #   \param message \type{string} The message to log.
    #   \exception NotImplementedError
    def log(self, log_type, message):
        raise NotImplementedError("Logger was not correctly implemented")
