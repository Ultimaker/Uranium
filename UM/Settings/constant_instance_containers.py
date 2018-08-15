# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from .EmptyInstanceContainer import EmptyInstanceContainer

#
# This file contains all constant instance containers.
#


# Instance of an empty container
EMPTY_CONTAINER_ID = "empty"
empty_container = EmptyInstanceContainer(EMPTY_CONTAINER_ID)


__all__ = ["EMPTY_CONTAINER_ID", "empty_container"]
