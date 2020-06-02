# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from typing import Optional, Dict, Any


class PluginObject:
    """Base class for objects that can be provided by a plugin.

    This class should be inherited by any class that can be provided
    by a plugin. Its only function is to serve as a mapping between
    the plugin and the object.
    """

    def __init__(self, *args, **kwags) -> None:
        self._plugin_id = None  # type: Optional[str]
        self._version = None  # type: Optional[str]
        self._metadata = {}  # type: Dict[str, Any]
        self._name = None  # type: Optional[str]

    #   This returns a globally unique id for this plugin object.
    #   It prepends it's set name (which should be locally (eg; within the plugin) unique) with the plugin_id, making it
    #   globally unique.
    def getId(self) -> str:
        result = self.getPluginId()
        if self._name:
            result += "_%s" % self._name
        return result

    def setPluginId(self, plugin_id: str) -> None:
        self._plugin_id = plugin_id

    #   The metadata of the plugin is set at the moment it is loaded.
    def setMetaData(self, metadata: Dict[str, Any]) -> None:
        self._metadata = metadata

    def getMetaData(self) -> Dict[str, Any]:
        return self._metadata

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

