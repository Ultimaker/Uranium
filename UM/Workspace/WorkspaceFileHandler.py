# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Logger import Logger
from UM.FileHandler.FileHandler import FileHandler


##  Central class for reading and writing workspaces.
#   This class is created by Application and handles reading and writing workspace files.
class WorkspaceFileHandler(FileHandler):
    def __init__(self):
        super().__init__("workspace_writer", "workspace_reader")

    def readerRead(self, reader, file_name, **kwargs):
        try:
            results = reader.read(file_name)
            return results
        except:
            Logger.logException("e", "An exception occured while loading workspace.")

        Logger.log("w", "Unable to load workspace %s", file_name)
        return None

    def _readLocalFile(self, file):
        from UM.FileHandler.ReadFileJob import ReadFileJob
        job = ReadFileJob(file.toLocalFile(), handler = self)
        job.finished.connect(self._readWorkspaceFinished)
        job.start()

    def _readWorkspaceFinished(self, job):
        # Add the loaded nodes to the scene.
        nodes = job.getResult()
        if nodes is not None:  # Job was not a failure.
            # Delete all old nodes.
            self._application.deleteAll()

            # Add the loaded nodes to the scene.
            nodes = job.getResult()
            for node in nodes:
                # We need to prevent circular dependency, so do some just in time importing.
                from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
                op = AddSceneNodeOperation(node, self._application.getController().getScene().getRoot())
                op.push()
                self._application.getController().getScene().sceneChanged.emit(node)