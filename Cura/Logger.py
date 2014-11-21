##  Abstract base class for logging classes.
class Logger(object):
    def __init__(self):
        super(Logger, self).__init__() # Call super to make multiple inheritence work.
        self._name = type(self).__name__ # Set name of the logger to it's class name
    
    def log(self, log_type, message):
        raise NotImplementedError('Logger was not correctly implemented')
