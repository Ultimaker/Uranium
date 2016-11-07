# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.FileHandler.FileHandler import FileHandler


##  Central class for reading and writing workspaces.
#   This class is created by Application and handles reading and writing workspace files.
class WorkspaceFileHandler(FileHandler):
    def __init__(self):
        super().__init__("workspace_writers", "workspace_readers")