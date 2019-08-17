# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import collections
import sys

##  Convenience class to simplify OS checking and similar platform-specific handling.
class Platform:

    ##  Get the platform type.
    @staticmethod
    def getType() -> int:
        platforms = collections.defaultdict(lambda: '4')  # Return 4 if the OS is not Windows, Linux or OSX
        platforms = {'win32': 1,    # Windows
                     'linux': 2,    # Linux
                     'darwin': 3,   # OSX
                    }
        return platforms[sys.platform]

    ##  Check to see if we are currently running on OSX.
    @staticmethod
    def isOSX() -> bool:
        return sys.platform == 'darwin'

    ##  Check to see if we are currently running on Windows.
    @staticmethod
    def isWindows() -> bool:
        return sys.platform == 'win32'

    ##  Check to see if we are currently running on Linux.
    @staticmethod
    def isLinux() -> bool:
        return sys.platform == 'linux'
