# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
from enum import Enum
from UM.PluginObject import PluginObject


class MeshReader(PluginObject):
    ##  Used as the return value of MeshReader.preRead.
    class PreReadResult(Enum):
        #The user has accepted the configuration dialog or there is no configuration dialog.
        #The plugin should load the mesh.
        accepted = 1
        #The user has cancelled the dialog so don't load the mesh.
        cancelled = 2
        #preRead has failed and no further processing should happen.
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
    def preRead(self, file_name):
        return MeshReader.PreReadResult.accepted

    ##  Read mesh data from file and returns a node that contains the data 
    #   Note that in some cases you can get an entire scene of nodes in this way (eg; 3MF)
    #
    #   \return node \type{SceneNode} or \type{list(SceneNode)} The SceneNode or SceneNodes read from file.
    def read(self, file_name):
        raise NotImplementedError("Reader plugin was not correctly implemented, no read was specified")
