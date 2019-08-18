# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional


##  Base class for objects that can be provided by a plugin.
#
#   This class should be inherited by any class that can be provided
#   by a plugin. Its only function is to serve as a mapping between
#   the plugin and the object.
class PluginObject:
    def __init__(self) -> None:
        self._plugin_id = None  # type: Optional[str]
        self._version = None  # type: Optional[str]

    def setPluginId(self, plugin_id: str) -> None:
        self._plugin_id = plugin_id

    def getPluginId(self) -> str:
        if not self._plugin_id:
            raise ValueError("The plugin ID needs to be set before the plugin can be used")
        return self._plugin_id

    def setVersion(self, version: str) -> None:
        self._version = version

    def getVersion(self) -> str:
        if not self._version:
            raise ValueError("The plugin version needs to be set before the plugin can be used")
        return self._version

