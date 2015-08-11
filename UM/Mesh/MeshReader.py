# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginObject import PluginObject

class MeshReader(PluginObject):
    def __init__(self):
        super().__init__()

    ##  Read mesh data from file and returns a node that contains the data 
    #   Note that in some cases you can get an entire scene of nodes in this way (eg; 3MF)
    #
    #   \return node \type{SceneNode} The scene node to write to the stream.
    def read(self, file_name):
        raise NotImplementedError("Reader plugin was not correctly implemented, no read was specified")
