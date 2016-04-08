# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject


##  Base class for mesh writer objects
class MeshWriter(PluginObject):
    class OutputMode:
        TextMode = 1
        BinaryMode = 2

    def __init__(self):
        super().__init__()
    
    ##  Output node to stream in such a way that it makes sense for the file format.
    #
    #   For example, in case of STL, it makes sense to go through all child nodes of
    #   node and write all those as transformed vertices to a single file.
    #
    #   \param stream \type{IOStream] The stream to output to.
    #   \param node \type{SceneNode} The scene node to write to the stream.
    def write(self, stream, node):
        raise NotImplementedError("Writer plugin was not correctly implemented, no write was specified")
