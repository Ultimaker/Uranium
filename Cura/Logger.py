##  Abstract base class for logging classes.
class Logger(object):
    def __init__(self):
        super(Logger, self).__init__() # Call super to make multiple inheritence work.
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
