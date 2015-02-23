class Logger:
    ##  Add a logger to the list.
    #   \param logger Logger
    @classmethod
    def addLogger(cls, logger):
        cls.__loggers.append(logger)

    ##  Get all loggers
    #   \returns List of Loggers
    @classmethod
    def getLoggers(cls):
        return cls.__loggers

    ##  Send a message of certain type to all loggers to be handled.
    #   \param log_type 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning)
    #   \param message String containing message to be logged
    #   \param message List of variables to be added to the message
    @classmethod
    def log(cls, log_type, message, *args):
        for logger in cls.__loggers:
            filled_message = message % args # Replace all the %s with the variables. Python formating is magic.
            logger.log(log_type, filled_message)

    __loggers = []

##  Abstract base class for log output classes.
class LogOutput():
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
    def log(self, log_type, message):
        raise NotImplementedError('Logger was not correctly implemented')
