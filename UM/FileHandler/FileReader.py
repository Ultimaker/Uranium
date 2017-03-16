# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
from enum import Enum
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

    def __init__(self):
        super().__init__()
        self._supported_extensions = []

    ##  Returns true if file_name can be processed by this plugin.
    #
    #   \return boolean indication if this plugin accepts the file specified.
    def acceptsFile(self, file_name):
        extension = os.path.splitext(file_name)[1]
        if extension.lower() in self._supported_extensions:
            return True
        return False

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
