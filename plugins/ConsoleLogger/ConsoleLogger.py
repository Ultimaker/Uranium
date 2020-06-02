# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import logging
from typing import Set

from UM.Logger import LogOutput

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
except ImportError:  # ModuleNotFoundError was new for 3.6 and we're still on 3.5
    from logging import Formatter
    logging_formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")


class ConsoleLogger(LogOutput):
    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(self._name) # Create python logger
        self._logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler() # Log to stream
        stream_handler.setFormatter(logging_formatter)
        self._logger.addHandler(stream_handler)
        self._show_once = set()  # type: Set[str]

    def log(self, log_type: str, message: str) -> None:
        """Log the message to console

        :param log_type: "e" (error), "i"(info), "d"(debug), "w"(warning) or "c"(critical) (can postfix with "_once")
        :param message: String containing message to be logged
        """

        if log_type == "w":  # Warning
            self._logger.warning(message)
        elif log_type == "i":  # Info
            self._logger.info(message)
        elif log_type == "e":  # Error
            self._logger.error(message)
        elif log_type == "d":
            self._logger.debug(message)
        elif log_type == "c":
            self._logger.critical(message)
        elif log_type.endswith("_once"):
            if message not in self._show_once:
                self._show_once.add(message)
                self.log(log_type[0], message)
        else:
            print("Unable to log. Received unknown type %s" % log_type)
