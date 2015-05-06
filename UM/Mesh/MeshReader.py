# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject

class MeshReader(PluginObject):
    def __init__(self):
        super().__init__()

    # Tries to read the file from specified file_name, returns None if it's uncessfull or unable to read.
    def read(self, file_name, storage_device):
        raise NotImplementedError("Reader plugin was not correctly implemented, no read was specified")
