# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.FileHandler.FileHandler import FileHandler


##  Central class for reading and writing workspaces.
#   This class is created by Application and handles reading and writing workspace files.
class WorkspaceFileHandler(FileHandler):
    def __init__(self):
        super().__init__("workspace_writer", "workspace_reader")

    def readerRead(self, reader, file_name, **kwargs):
        pass

    def _readLocalFile(self, file):
        from UM.FileHandler.ReadFileJob import ReadFileJob
        job = ReadFileJob(file.toLocalFile(), handler = self)
        job.finished.connect(self._readWorkspaceFinished)
        job.start()

    def _readWorkspaceFinished(self, job):
        pass
