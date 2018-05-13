# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict, List, Optional, TYPE_CHECKING

import UM.Decorators
from UM.Logger import Logger
from UM.Signal import Signal
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext

if TYPE_CHECKING:
    from UM.Application import Application
    from UM.Settings.InstanceContainer import InstanceContainer
    from UM.Settings.SettingDefinition import SettingDefinition #For typing.

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
    #   \param ignored_metadata_keys A set of keys that should be ignored when
    #   it serializes the metadata.
    #
    #   \return \type{string} A string representation of this container.
    def serialize(self, ignored_metadata_keys: Optional[set] = None) -> str:
        pass

    ##  Deserialize the container from a string representation.
    #
    #   This should replace the contents of this container with those in the serialized
    #   representation.
    #
    #   \param serialized A serialized string containing a container that should be deserialized.
    def deserialize(self, serialized: str, file_name: Optional[str] = None) -> str:
        return self._updateSerialized(serialized, file_name = file_name)

    ##  Deserialize just the metadata from a string representation.
    #
    #   \param serialized A string representing one or more containers that
    #   should be deserialized.
    #   \param container_id The ID of the (base) container is already known and
    #   provided here.
    #   \return A list of the metadata of all containers found in the document.
    @classmethod
    def deserializeMetadata(cls, serialized: str, container_id: str) -> List[Dict[str, Any]]:
        Logger.log("w", "Class {class_name} hasn't implemented deserializeMetadata!".format(class_name = cls.__name__))
        return []

    ##  Updates the given serialized data to the latest version.
    @classmethod
    def _updateSerialized(cls, serialized: str, file_name: Optional[str] = None) -> str:
        configuration_type = cls.getConfigurationTypeFromSerialized(serialized)
        version = cls.getVersionFromSerialized(serialized)
        if configuration_type is not None and version is not None:
            from UM.VersionUpgradeManager import VersionUpgradeManager
            result = VersionUpgradeManager.getInstance().updateFilesData(configuration_type, version,
                                                                         [serialized],
                                                                         [file_name if file_name else ""])
            if result is not None:
                serialized = result.files_data[0]
        return serialized

    @classmethod
    def getLoadingPriority(cls) -> int:
        return 9001 #Goku wins!

    ##  Gets the configuration type of the given serialized data. (used by __updateSerialized())
    @classmethod
    def getConfigurationTypeFromSerialized(cls, serialized: str) -> Optional[str]:
        pass

    ##  Gets the version of the given serialized data. (used by __updateSerialized())
    @classmethod
    def getVersionFromSerialized(cls, serialized: str) -> Optional[int]:
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
    def findDefinitions(self, **kwargs: Any) -> "SettingDefinition":
        raise NotImplementedError()


##  Shared interface between setting container types
#
@UM.Decorators.interface
class ContainerRegistryInterface:
    def findContainers(self, *, ignore_case: bool = False, **kwargs: Any) -> List[ContainerInterface]:
        raise NotImplementedError()

    def findDefinitionContainers(self, **kwargs: Any) -> List[DefinitionContainerInterface]:
        raise NotImplementedError()

    @classmethod
    def getApplication(cls) -> "Application":
        raise NotImplementedError()

    def getEmptyInstanceContainer(self) -> "InstanceContainer":
        raise NotImplementedError()

    def isReadOnly(self, container_id: str) -> bool:
        raise NotImplementedError()