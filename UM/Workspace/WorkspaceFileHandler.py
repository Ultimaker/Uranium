# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry


##  Central class for reading and writing workspaces.
#   This class is created by Application and handles reading and writing workspace files.
class WorkspaceFileHandler:
    def __init__(self):
        super().__init__()

        self._workspace_readers = {}
        self._workspace_writers = {}

        PluginRegistry.addType("workspace_readers", self.addReader)
        PluginRegistry.addType("workspace_writers", self.addWriter)

    ##  Register a workspace reader
    #   \param reader \type{WorkspaceReader} The WorkspaceReader to register.
    def addReader(self, reader):
        self._workspace_readers[reader.getsPluginId()] = reader

    ##  Register a workspace writer
    #   \param reader \type{WorkspaceWriter} The WorkspaceWriter to register.
    def addWriter(self, writer):
        self._workspace_writers[writer.getPluginId()] = writer