from Cura.Logger import Logger
import logging

class FileLogger(Logger):
    def __init__(self, file_name):
        super(FileLogger,self).__init__()
        self._logger =  logging.getLogger(self._name) #Create python logger 
        self._logger.setLevel(logging.DEBUG)
        if(".log" in file_name):
            file_handler = logging.FileHandler('file_name')
            format_handler = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(format_handler)
            self._logger.addHandler(file_handler)
        else:
            pass #TODO, add handling
    
        
    def log(self, log_type, message):
        pass