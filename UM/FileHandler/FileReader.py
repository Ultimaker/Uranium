# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from enum import IntEnum
from typing import Any

from .FileHandler import FileHandler


class FileReader(FileHandler):

    # Used as the return value of FileReader.preRead.
    class PreReadResult(IntEnum):
        # The user has accepted the configuration dialog or there is no configuration dialog.
        # The plugin should load the data.
        accepted = 1
        # The user has cancelled the dialog so don't load the data.
        cancelled = 2
        # preRead has failed and no further processing should happen.
        failed = 3

    def acceptsFile(self, file_name: str) -> bool:
        file_name_lower = file_name.lower()
        is_supported = False
        for extension in self._supported_extensions:
            if file_name_lower.endswith(extension):
                is_supported = True
                break
        return is_supported

    def preRead(self, file_name: str, *args: Any, **kwargs: Any) -> PreReadResult:
        return FileReader.PreReadResult.accepted

    def read(self, file_name: str, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Reader plugin was not correctly implemented, no read was specified")
