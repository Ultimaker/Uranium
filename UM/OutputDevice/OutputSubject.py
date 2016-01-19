# Copyright (c) 2015 Ruben Dulek, Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from enum import Enum

##  Defines the different possible outputs for output devices.
#
#   The output subject that is selected will determine where an output device
#   gets its list of available extensions, where it gets its writers, and so on.
class OutputSubject(Enum):
    ##  Writes a serialised representation of a mesh.
    MESH = 1

    ##  Writes the output of the backend.
    BACKEND_OUTPUT = 2