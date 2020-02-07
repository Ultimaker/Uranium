# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import sys


class Platform:
    """Convenience class to simplify OS checking and similar platform-specific handling."""

    class PlatformType:
        Windows = 1
        Linux = 2
        OSX = 3
        Other = 4

    @classmethod
    def isOSX(cls) -> bool:
        """Check to see if we are currently running on OSX."""

        return cls.__platform_type == cls.PlatformType.OSX

    @classmethod
    def isWindows(cls) -> bool:
        """Check to see if we are currently running on Windows."""

        return cls.__platform_type == cls.PlatformType.Windows

    @classmethod
    def isLinux(cls) -> bool:
        """Check to see if we are currently running on Linux."""

        return cls.__platform_type == cls.PlatformType.Linux

    @classmethod
    def getType(cls) -> int:
        """Get the platform type."""

        return cls.__platform_type

    __platform_type = PlatformType.Other
    if sys.platform == "win32":
        __platform_type = PlatformType.Windows
    elif sys.platform == "linux":
        __platform_type = PlatformType.Linux
    elif sys.platform == "darwin":
        __platform_type = PlatformType.OSX
