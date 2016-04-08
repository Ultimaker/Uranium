# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject


class ProfileReader(PluginObject):
    def __init__(self):
        super().__init__()

    ##  Read profile data from a file and return a filled profile.
    #
    #   \return node \type{Profile} The profile that was obtained from the file.
    def read(self, file_name):
        raise NotImplementedError("Profile reader plugin was not correctly implemented. The read function was not implemented.")
