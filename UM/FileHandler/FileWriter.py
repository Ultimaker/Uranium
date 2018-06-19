# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from enum import IntEnum
from typing import Any

from .FileHandler import FileHandler


class FileWriter(FileHandler):

    class OutputMode(IntEnum):
        TextMode = 1
        BinaryMode = 2

    def write(self, stream, data, *args, **kwargs) -> Any:
        raise NotImplementedError("Writer plugin was not correctly implemented, no write was specified")
