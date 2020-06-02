# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


class WriteRequestFailedError(Exception):
    """Base class for error raised by OutputDevice::requestWrite()

    This class serves as a base class for more specialized errors raised
    by OutputDevice::requestWrite(). Additionally, it can be raised whenever
    an error occurs for which no specialized error is available.
    """

    pass


class UserCanceledError(WriteRequestFailedError):
    """The user canceled the operation."""

    pass


class PermissionDeniedError(WriteRequestFailedError):
    """Permission was denied when trying to write to the device."""

    pass


class DeviceBusyError(WriteRequestFailedError):
    """The device is busy and cannot accept write requests at the moment."""

    pass
