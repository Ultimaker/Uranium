from Cura.Logger import Logger
import logging

class FileLogger(Logger):
    def __init__(self, file_name):
        super(FileLogger,self).__init__()
        self._logger =  logging.getLogger(self._name) #Create python logger 
        self._logger.setLevel(logging.DEBUG)
        self.setFileName(file_name)
        
        
    def setFileName(self, file_name):
        if(".log" in file_name):
            file_handler = logging.FileHandler(file_name)
            format_handler = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(format_handler)
            self._logger.addHandler(file_handler)
        else:
            pass #TODO, add handling
        
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