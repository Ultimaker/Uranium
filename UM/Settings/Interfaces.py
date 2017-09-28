# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List, Dict, Any, Optional

import UM.Decorators
from UM.Signal import Signal
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext


##  Shared interface between setting container types
#
@UM.Decorators.interface
class ContainerInterface:
    ##  Get the ID of the container.
    #
    #   The ID should be unique, machine readable and machine writable. It is
    #   intended to be used for example when referencing the container in
    #   configuration files or when writing a file to disk.
    #
    #   \return \type{string} The unique ID of this container.
    def getId(self) -> str:
        pass

    ##  Get the human-readable name of this container.
    #
    #   This should return a human-readable name for the container, that can be
    #   used in the interface.
    #
    #   \return \type{string} The name of this container.
    def getName(self) -> str:
        pass

    ##  Get whether the container item is stored on a read only location in the filesystem.
    #
    #   \return True if the specified item is stored on a read-only location
    #   in the filesystem
    def isReadOnly(self) -> bool:
        pass

    ##  Get all metadata of this container.
    #
    #   This returns a dictionary containing all the metadata for this container.
    #   How this metadata is used depends on the application.
    #
    #   \return \type{dict} The metadata for this container.
    def getMetaData(self) -> Dict[str, Any]:
        pass

    ##  Get the value of a single metadata entry.
    #
    #   \param entry \type{string} The key of the metadata to retrieve.
    #   \param default The default value to return if the entry cannot be found.
    #
    #   \return The value of the metadata corresponding to `name`, or `default`
    #           when the entry could not be found.
    def getMetaDataEntry(self, entry: str, default: Any = None) -> Any:
        pass

    ##  Get the value of a property of the container item.
    #
    #   \param key \type{string} The key of the item to retrieve a property from.
    #   \param name \type{string} The name of the property to retrieve.
    #
    #   \return The specified property value of the container item corresponding to key, or None if not found.
    def getProperty(self, key: str, property_name: str, context: Optional[PropertyEvaluationContext] = None) -> Any:
        pass

    ##  Get whether the container item has a specific property.
    #
    #   \param key The key of the item to check the property from.
    #   \param name The name of the property to check for.
    #
    #   \return True if the specified item has the property, or False if it
    #   doesn't.
    def hasProperty(self, key: str, property_name: str) -> bool:
        pass

    ##  Serialize this container to a string.
    #
    #   The serialized representation of the container can be used to write the
    #   container to disk or send it over the network.
    #
    #   \param ignored_metadata_keys A list of keys that should be ignored when it serializes the metadata.
    #
    #   \return \type{string} A string representation of this container.
    def serialize(self, ignored_metadata_keys: Optional[List] = None) -> str:
        pass

    ##  Deserialize the container from a string representation.
    #
    #   This should replace the contents of this container with those in the serialized
    #   represenation.
    #
    #   \param serialized A serialized string containing a container that should be deserialized.
    def deserialize(self, serialized: str) -> str:
        return self.__updateSerialized(serialized)

    ##  Updates the given serialized data to the latest version.
    def __updateSerialized(self, serialized: str) -> str:
        configuration_type = self.getConfigurationTypeFromSerialized(serialized)
        version = self.getVersionFromSerialized(serialized)
        if configuration_type is not None and version is not None:
            from UM.VersionUpgradeManager import VersionUpgradeManager
            result = VersionUpgradeManager.getInstance().updateFilesData(configuration_type, version,
                                                                         [serialized], [""])
            if result is not None:
                serialized = result.files_data[0]
        return serialized

    @classmethod
    def getLoadingPriority(cls) -> int:
        return 9001

    ##  Gets the configuration type of the given serialized data. (used by __updateSerialized())
    def getConfigurationTypeFromSerialized(self, serialized: str) -> Optional[str]:
        pass

    ##  Gets the version of the given serialized data. (used by __updateSerialized())
    def getVersionFromSerialized(self, serialized: str) -> Optional[int]:
        pass

    ##  Get the path used to create this InstanceContainer.
    def getPath(self) -> str:
        pass

    ##  Set the path used to create this InstanceContainer
    def setPath(self, path: str) -> None:
        pass

    propertyChanged = None   # type: Signal

    metaDataChanged = None  # type: Signal


class DefinitionContainerInterface(ContainerInterface):
    pass


##  Shared interface between setting container types
#
@UM.Decorators.interface
class ContainerRegistryInterface:
    def findDefinitionContainers(self, **kwargs: Any) -> List[DefinitionContainerInterface]: pass
