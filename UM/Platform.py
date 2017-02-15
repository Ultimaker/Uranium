# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import sys


##  Convenience class to simplify OS checking and similar platform-specific handling.
class Platform:
    class PlatformType:
        Windows = 1
        Linux = 2
        OSX = 3
        Other = 4

    ##  Check to see if we are currently running on OSX.
    @classmethod
    def isOSX(cls) -> bool:
        return cls.__platform_type == cls.PlatformType.OSX

    ##  Check to see if we are currently running on Windows.
    @classmethod
    def isWindows(cls) -> bool:
        return cls.__platform_type == cls.PlatformType.Windows

    ##  Check to see if we are currently running on Linux.
    @classmethod
    def isLinux(cls) -> bool:
        return cls.__platform_type == cls.PlatformType.Linux

    ##  Get the platform type.
    @classmethod
    def getType(cls) -> int:
        return cls.__platform_type

    __platform_type = PlatformType.Other
    if sys.platform == "win32":
        __platform_type = PlatformType.Windows
    elif sys.platform == "linux":
        __platform_type = PlatformType.Linux
    elif sys.platform == "darwin":
        __platform_type = PlatformType.OSX
