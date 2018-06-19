# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Logging.Logger import LogOutput

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
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler() # Log to stream
        stream_handler.setFormatter(logging_formatter)
        self._logger.addHandler(stream_handler)
