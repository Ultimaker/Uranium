# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.FileHandler.FileWriter import FileWriter


class WorkspaceWriter(FileWriter):
    def __init__(self):
        super().__init__()

    def write(self, stream, node):
        pass