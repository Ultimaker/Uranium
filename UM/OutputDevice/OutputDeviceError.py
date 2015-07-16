# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

class WriteRequestFailedError(Exception):
    pass

class UserCancelledError(WriteRequestFailedError):
    pass

class PermissionDeniedError(WriteRequestFailedError):
    pass

class DeviceBusyError(WriteRequestFailedError):
    pass
