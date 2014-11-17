class Logger(object):
    def __init__(self):
        self._name = type(self).__name__ # Set name of the logger to it's class name
    
    def log(self, log_type, message):
        raise NotImplementedError('Logger was not correctly implemented')