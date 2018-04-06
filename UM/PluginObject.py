# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.


##  Base class for objects that can be provided by a plugin.
#
#   This class should be inherited by any class that can be provided
#   by a plugin. Its only function is to serve as a mapping between
#   the plugin and the object.

class PluginObject:
    def __init__(self):
        self._plugin_id = None
        self._version = None

    def getPluginId(self):
        return self._plugin_id

    def setPluginId(self, plugin_id):
        self._plugin_id = plugin_id

    def setVersion(self, version: str):
        self._version = version

    def getVersion(self) -> str:
        return self._version
