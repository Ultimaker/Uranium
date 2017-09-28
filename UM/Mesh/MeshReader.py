# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
from enum import Enum
from UM.FileHandler.FileReader import FileReader


class MeshReader(FileReader):
    def __init__(self):
        super().__init__()

    ##  Read mesh data from file and returns a node that contains the data 
    #   Note that in some cases you can get an entire scene of nodes in this way (eg; 3MF)
    #
    #   \return node \type{SceneNode} or \type{list(SceneNode)} The SceneNode or SceneNodes read from file.
    def read(self, file_name):
        raise NotImplementedError("MeshReader plugin was not correctly implemented, no read was specified")
