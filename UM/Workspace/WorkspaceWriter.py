# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.FileHandler.FileWriter import FileWriter


class WorkspaceWriter(FileWriter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def write(self, stream, node):
        raise NotImplementedError("WorkspaceWriter plugin was not correctly implemented, no write was specified")