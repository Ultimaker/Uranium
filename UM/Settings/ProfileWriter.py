# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject

##  Base class for profile writer plugins.
#
#   This class defines a write() function to write profiles to files with.
class ProfileWriter(PluginObject):
    ##  Initialises the profile writer.
    #
    #   This currently doesn't do anything since the writer is basically static.
    def __init__(self):
        super().__init__()
    
    ##  Writes a profile to the specified stream.
    #
    #   For example, the stream could be a file stream. The profile writer then
    #   writes its own file format to the specified file.
    #
    #   \param stream \type{IOStream} The stream to output to.
    #   \param profile \type{Profile} The profile to write to the stream.
    def write(self, stream, node):
        raise NotImplementedError("Profile writer plugin was not correctly implemented. No write was specified.")
