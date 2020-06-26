# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Optional
import uuid

from UM.PluginObject import PluginObject
from UM.Settings.Interfaces import ContainerInterface

##  Test container type to test adding new container types with.
class ContainerTestPlugin(ContainerInterface, PluginObject):
    ##  Initialise a new definition container.
    #
    #   The container will have the specified ID and all metadata in the
    #   provided dictionary.
    def __init__(self):
        self._id = str(uuid.uuid4())
        self._metadata = { }
        self._plugin_id = "TestContainerPlugin"

    ##  Gets the ID that was provided at initialisation.
    #
    #   \return The ID of the container.
    def getId(self):
        return self._id

    ##  Gets all metadata of this container.
    #
    #   This returns the metadata dictionary that was provided in the
    #   constructor of this test container.
    #
    #   \return The metadata for this container.
    def getMetaData(self):
        return self._metadata

    ##  Gets a metadata entry from the metadata dictionary.
    #
    #   \param key The key of the metadata entry.
    #   \return The value of the metadata entry, or None if there is no such
    #   entry.
    def getMetaDataEntry(self, entry, default = None):
        if entry in self._metadata:
            return self._metadata[entry]
        return default

    ##  Gets a human-readable name for this container.
    #
    #   \return Always returns "TestContainer".
    def getName(self):
        return "TestContainer"

    ##  Mock get path
    def getPath(self):
        return "/path/to/the/light/side"

    ##  Mock set path
    def setPath(self, path):
        pass

    ##  Get whether the container item is stored on a read only location in the filesystem.
    #
    #   \return Always returns False
    def isReadOnly(self):
        return False

    def getAllKeys(self):
        pass

    ##  Get the value of a property of a container item.
    #
    #   Since this test container cannot contain any items, it always returns
    #   None.
    #
    #   \return Always returns None.
    def getProperty(self, key, property_name, context = None):
        pass

    def setProperty(self, key: str, property_name: str, property_value: Any, container: "ContainerInterface" = None, set_from_cache: bool = False) -> None:
        pass

    def hasProperty(self, key, property_name):
        pass

    ##  Serializes the container to a string representation.
    #
    #   This method is not implemented in the mock container.
    def serialize(self, ignored_metadata_keys=set()):
        raise NotImplementedError()

    # Should return false (or even throw an exception) if trust (or other verification) is invalidated.
    def _trustHook(self, file_name: Optional[str]) -> bool:
        raise NotImplementedError()

    ##  Deserializes the container from a string representation.
    #
    #   This method is not implemented in the mock container.
    def deserialize(self, serialized, file_name: Optional[str] = None):
        raise NotImplementedError()

    @classmethod
    def getConfigurationTypeFromSerialized(cls, serialized):
        raise NotImplementedError()

    @classmethod
    def getVersionFromSerialized(cls, serialized):
        raise NotImplementedError()

    def isDirty(self):
        return True

    def setDirty(self, dirty):
        pass

    metaDataChanged = None  # type: Signal
