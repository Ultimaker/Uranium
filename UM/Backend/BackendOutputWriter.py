# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject

##  Base class for output writer plugin objects.
class BackendOutputWriter(PluginObject):
    def __init__(self):
        super().__init__()

    ##  Write the specified backend output to a stream in the correct file
    #   format.
    #
    #   This should take the output of the backend from the scene and convert it
    #   to the correct file format. For example, in the case of g-code, it may
    #   post-process the g-code before writing it to the file.
    #
    #   \param stream \type{IOStream} The stream to output to.
    #   \param scene \type{SceneNode} The scene node whose output to write to
    #   the stream.
    def write(self, stream, scene):
        raise NotImplementedError("Backend output writer plugin was not correctly implemented. No write was specified.")
