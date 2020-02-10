# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from UM.PluginObject import PluginObject


class FileWriter(PluginObject):
    """Base class for writer objects"""

    class OutputMode:
        TextMode = 1
        BinaryMode = 2

    def __init__(self, add_to_recent_files: bool = True, *args, **kwargs) -> None:
        super().__init__()
        self._information = ""  # type: str

        # Indicates if the file should be added to the "recent files" list if it's saved successfully.
        self._add_to_recent_files = add_to_recent_files  # type: bool

    def getAddToRecentFiles(self) -> bool:
        return self._add_to_recent_files

    def write(self, stream, data, mode = OutputMode.TextMode):
        raise NotImplementedError("Writer plugin was not correctly implemented, no write was specified")

    def setInformation(self, information_message: str):
        self._information = information_message

    def getInformation(self) -> str:
        return self._information
