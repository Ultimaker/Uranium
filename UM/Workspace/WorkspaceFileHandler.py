# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, QUrl #For typing.
from typing import Optional

from UM.Logger import Logger
from UM.FileHandler.FileHandler import FileHandler
from UM.FileHandler.ReadFileJob import ReadFileJob  # For typing.
from typing import TYPE_CHECKING, cast

from UM.Workspace.WorkspaceReader import WorkspaceReader

if TYPE_CHECKING:
    from UM.Qt.QtApplication import QtApplication


##  Central class for reading and writing workspaces.
#   This class is created by Application and handles reading and writing workspace files.
class WorkspaceFileHandler(FileHandler):
    def __init__(self, application: "QtApplication", writer_type: str = "workspace_writer", reader_type: str = "workspace_reader", parent: QObject = None) -> None:
        super().__init__(application, writer_type, reader_type, parent)
        self.workspace_reader = None  # type: Optional[WorkspaceReader]

    def readerRead(self, reader: WorkspaceReader, file_name: str, **kwargs):
        self.workspace_reader = reader
        results = None
        try:
            results = reader.read(file_name)
        except Exception:
            Logger.logException("w", "An exception occurred while loading workspace [%s]" % file_name)

        return results

    def _readLocalFile(self, file: QUrl) -> None:
        from UM.FileHandler.ReadFileJob import ReadFileJob
        job = ReadFileJob(file.toLocalFile(), handler = self)
        job.finished.connect(self._readWorkspaceFinished)
        job.start()

    def _readWorkspaceFinished(self, job: ReadFileJob) -> None:
        # Add the loaded nodes to the scene.
        result = job.getResult()
        if isinstance(result, tuple):
            nodes, metadata = result
        else:
            nodes = result
            metadata = {}

        if nodes is not None:  # Job was not a failure.
            self._application.resetWorkspace()
            for node in nodes:
                # We need to prevent circular dependency, so do some just in time importing.
                from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
                op = AddSceneNodeOperation(node, self._application.getController().getScene().getRoot())
                op.push()

            self._application.getWorkspaceMetadataStorage().setAllData(metadata)
            self._application.workspaceLoaded.emit(cast(WorkspaceReader, self.workspace_reader).workspaceName())
