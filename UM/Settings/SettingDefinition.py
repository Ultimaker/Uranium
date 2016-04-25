# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

class SettingDefinition:
    def __init__(self, key, container):
        self._key = key
        self._container = container

    def getKey(self):
        return self._key

    def getContainer(self):
        return self._container

    def serialize(self):
        pass

    def deserialize(self, serialized):
        pass
