# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.


##  Base class for error raised by OutputDevice::requestWrite()
#
#   This class serves as a base class for more specialized errors raised
#   by OutputDevice::requestWrite(). Additionally, it can be raised whenever
#   an error occurs for which no specialized error is available.
class WriteRequestFailedError(Exception):
    pass


##  The user canceled the operation.
class UserCanceledError(WriteRequestFailedError):
    pass


##  Permission was denied when trying to write to the device.
class PermissionDeniedError(WriteRequestFailedError):
    pass


##  The device is busy and cannot accept write requests at the moment.
class DeviceBusyError(WriteRequestFailedError):
    pass
