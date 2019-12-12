# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from enum import Enum
from typing import List
from UM.PluginObject import PluginObject


class FileReader(PluginObject):
    ##  Used as the return value of FileReader.preRead.
    class PreReadResult(Enum):
        # The user has accepted the configuration dialog or there is no configuration dialog.
        # The plugin should load the data.
        accepted = 1
        # The user has cancelled the dialog so don't load the data.
        cancelled = 2
        # preRead has failed and no further processing should happen.
        failed = 3

    def __init__(self) -> None:
        super().__init__()
        self._supported_extensions = []  # type: List[str]

    ##  Returns true if file_name can be processed by this plugin.
    #
    #   \return boolean indication if this plugin accepts the file specified.
    def acceptsFile(self, file_name):
        file_name_lower = file_name.lower()
        is_supported = False
        for extension in self._supported_extensions:
            if file_name_lower.endswith(extension):
                is_supported = True
        return is_supported

    ##  Executed before reading the file. This is used, for example, to display an import
    #   configuration dialog. If a plugin displays such a dialog,
    #   this function should block until it has been closed.
    #
    #   \return \type{PreReadResult} indicating if the user accepted or canceled the dialog.
    def preRead(self, file_name, *args, **kwargs):
        return FileReader.PreReadResult.accepted

    ##  Read mesh data from file and returns a node that contains the data
    #
    #   \return data read.
    def read(self, file_name):
        raise NotImplementedError("Reader plugin was not correctly implemented, no read was specified")
