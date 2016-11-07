# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.FileHandler.FileReader import FileReader


class WorkspaceReader(FileReader):
    def __init__(self):
        super().__init__()

    ##  Read an entire workspace
    def read(self, file_name):
        pass