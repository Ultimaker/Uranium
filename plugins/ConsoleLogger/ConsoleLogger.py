from Cura.Logger import Logger
import logging

class ConsoleLogger(Logger):
    def __init__(self):
        super(ConsoleLogger,self).__init__()
        self._logger = logging.getLogger(self._name) #Create python logger 
        self._logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(stream_handler)
        
    def log(self, log_type, message):
        if(log_type == 'w'): # Warning
            self._logger.warning(message)
        elif(log_type == 'i'): # Info
            self._logger.info(message)
        elif(log_type == 'e'): # Error
            self._logger.error(message)
        elif(log_type == 'd'):
            self._logger.debug(message)
        else:
            print("Unable to log")