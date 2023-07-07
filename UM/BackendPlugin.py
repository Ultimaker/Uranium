# Copyright (c) 2023 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


from UM.PluginObject import PluginObject
import collections
from typing import Optional, Any, Callable, List, Dict


class BackendPlugin(PluginObject):

    def __init__(self) -> None:
        super().__init__()