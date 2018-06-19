# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.


class VersionUpgrade:
    pass


class FormatException(Exception):
    def __init__(self, message: str, file: str = ""):
        self._message = message
        self._file = file

    def __str__(self) -> str:
        return "Exception parsing " + self._file + ": " + self._message


class InvalidVersionException(Exception):
    pass
