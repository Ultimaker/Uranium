# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.
from UM.PluginObject import PluginObject


##  Base class for writer objects
class FileWriter(PluginObject):
    class OutputMode:
        TextMode = 1
        BinaryMode = 2

    def __init__(self):
        super().__init__()

    def write(self, stream, data):
        raise NotImplementedError("Writer plugin was not correctly implemented, no write was specified")