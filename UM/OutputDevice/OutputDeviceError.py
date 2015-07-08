# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

class ErrorCodes:
    UserCanceledError = 1
    DeviceBusyError = 2

class WriteRequestFailedError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message
