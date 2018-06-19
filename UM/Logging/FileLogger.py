# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Logging.Logger import LogOutput
from UM.Resources import Resources

import logging


class FileLogger(LogOutput):
    def __init__(self, file_name):
        super().__init__()
        self._logger = logging.getLogger(self._name)  # Create python logger
        self._logger.setLevel(logging.DEBUG)

        # Do not try to save to the app dir as it may not be writeable or may not be the right
        # location to save the log file. Instead, try and save in the settings location since
        # that should be writeable.
        self.setFileName(Resources.getStoragePath(Resources.Resources, file_name))

    def setFileName(self, file_name):
        if ".log" in file_name:
            file_handler = logging.FileHandler(file_name, encoding = "utf-8")
            format_handler = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(format_handler)
            self._logger.addHandler(file_handler)
        else:
            pass  # TODO, add handling
