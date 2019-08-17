# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import collections
import sys

##  Convenience class to simplify OS checking and similar platform-specific handling.
class Platform:

    platforms = collections.defaultdict(lambda : '4')  # Return 4 if the OS is not Windows, Linux or OSX
    platforms = {'win32': 1,    #Windows
                 'linux': 2,    #Linux
                 'darwin': 3,   #OSX
                }

    __platform_type = platforms[sys.platform]

    ##  Get the platform type.
    @classmethod
    def getType(cls) -> int:
        return cls.__platform_type

    ##  Check to see if we are currently running on OSX.
    @classmethod
    def isOSX(cls) -> bool:
        return cls.__platform_type == cls.platforms['darwin']

    ##  Check to see if we are currently running on Windows.
    @classmethod
    def isWindows(cls) -> bool:
        return cls.__platform_type == cls.platforms['win32']

    ##  Check to see if we are currently running on Linux.
    @classmethod
    def isLinux(cls) -> bool:
        return cls.__platform_type == cls.platforms['linux']
