# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.FileHandler.FileWriter import FileWriter


class WorkspaceWriter(FileWriter):
    def __init__(self, add_to_recent_files: bool = True) -> None:
        super().__init__(add_to_recent_files)

    def write(self, stream, node, mode = FileWriter.OutputMode.BinaryMode):
        raise NotImplementedError("WorkspaceWriter plugin was not correctly implemented, no write was specified")