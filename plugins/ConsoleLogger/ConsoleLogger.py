# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import LogOutput
from UM.Preferences import Preferences

import logging

try:
    from colorlog import ColoredFormatter
    logging_formatter = ColoredFormatter("%(purple)s%(asctime)s%(reset)s - %(log_color)s%(levelname)s%(reset)s - %(white)s%(message)s%(reset)s",
                                         log_colors = {'DEBUG': 'cyan',
                                                       'INFO': 'green',
                                                       'WARNING': 'yellow',
                                                       'ERROR': 'red',
                                                       'CRITICAL': 'red,bg_white',
                                                       },
                                         )
except:
    from logging import Formatter
    logging_formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")

class ConsoleLogger(LogOutput):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self._name) #Create python logger 
        self._logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler() # Log to stream
        stream_handler.setFormatter(logging_formatter)
        self._logger.addHandler(stream_handler)
    
    ##  Log the message to console
    #   \param log_type "e" (error) , "i"(info), "d"(debug) or "w"(warning)
    #   \param message String containing message to be logged
    def log(self, log_type, message):
        preference = Preferences.getInstance().getValue("logger/log_level_console")
        try:
            log_level_console = int(preference)
        except:
            log_level_console = 50

        if log_type == "c" and log_level_console >= 50: # Critical
            self._logger.critical(message)
        elif log_type == "e" and log_level_console >= 40: # Error
            self._logger.error(message)
        elif log_type == "w" and log_level_console >= 30: # Warning
            self._logger.warning(message)
        elif log_type == "i" and log_level_console >= 20: # Info
            self._logger.info(message)
        elif log_type == "d" and log_level_console >= 10: # Debug
            self._logger.debug(message)
        elif log_type not in ("c","e","w","i","d"):
            print("Unable to log. Received unknown type %s" % log_type)
