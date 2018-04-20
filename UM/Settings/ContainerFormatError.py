# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

##  A marker exception to indicate that something went wrong in deserialising a
#   container because the file is corrupt.
class ContainerFormatError(Exception):
    pass