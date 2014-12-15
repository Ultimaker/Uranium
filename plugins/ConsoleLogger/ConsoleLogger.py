from UM.Logger import LogOutput

import logging

class ConsoleLogger(LogOutput):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self._name) #Create python logger 
        self._logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler() # Log to stream
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(stream_handler)
    
    ##  Log the message to console
    #   \param log_type 'e' (error) , 'i'(info), 'd'(debug) or 'w'(warning)
    #   \param message String containing message to be logged
    def log(self, log_type, message):
        if(log_type == 'w'): # Warning
            self._logger.warning(message)
        elif(log_type == 'i'): # Info
            self._logger.info(message)
        elif(log_type == 'e'): # Error
            self._logger.error(message)
        elif(log_type == 'd'):
            self._logger.debug(message)
        elif(log_type == 'c'):
            self._logger.critical(message)
        else:
            print("Unable to log")
