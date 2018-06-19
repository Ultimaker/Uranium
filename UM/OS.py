# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from enum import IntEnum
import sys


##  Convenience class to simplify OS checking and similar platform-specific handling.
class OS:
    class OSType(IntEnum):
        Windows = 1
        Linux = 2
        OSX = 3
        Other = 4

    ##  Check to see if we are currently running on OSX.
    @classmethod
    def isOSX(cls) -> bool:
        return cls.__platform_type == cls.OSType.OSX

    ##  Check to see if we are currently running on Windows.
    @classmethod
    def isWindows(cls) -> bool:
        return cls.__platform_type == cls.OSType.Windows

    ##  Check to see if we are currently running on Linux.
    @classmethod
    def isLinux(cls) -> bool:
        return cls.__platform_type == cls.OSType.Linux

    ##  Get the platform type.
    @classmethod
    def getType(cls) -> OSType:
        return cls.__platform_type

    __platform_type = OSType.Other
    if sys.platform == "win32":
        __platform_type = OSType.Windows
    elif sys.platform == "linux":
        __platform_type = OSType.Linux
    elif sys.platform == "darwin":
        __platform_type = OSType.OSX
