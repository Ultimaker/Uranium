# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

import UM.Decorators
from UM.Logger import Logger
from UM.Signal import Signal
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext

if TYPE_CHECKING:
    from UM.Application import Application
    from UM.Settings.InstanceContainer import InstanceContainer
    from UM.Settings.SettingDefinition import SettingDefinition


@UM.Decorators.interface
class ContainerInterface:
    """Shared interface between setting container types"""


    def __init__(self, *args, **kwargs):
        pass

    def getId(self) -> str:
        """Get the ID of the container.

        The ID should be unique, machine readable and machine writable. It is
        intended to be used for example when referencing the container in
        configuration files or when writing a file to disk.

        :return: The unique ID of this container.
        """

        pass

    def getName(self) -> str:
        """Get the human-readable name of this container.

        This should return a human-readable name for the container, that can be
        used in the interface.

        :return: The name of this container.
        """

        pass

    def getMetaData(self) -> Dict[str, Any]:
        """Get all metadata of this container.

        This returns a dictionary containing all the metadata for this container.
        How this metadata is used depends on the application.

        :return: The metadata for this container.
        """

        pass

    def getMetaDataEntry(self, entry: str, default: Any = None) -> Any:
        """Get the value of a single metadata entry.

        :param entry: The key of the metadata to retrieve.
        :param default: The default value to return if the entry cannot be found.

        :return: The value of the metadata corresponding to `name`, or `default`
        when the entry could not be found.
        """

        pass

    def getProperty(self, key: str, property_name: str, context: Optional[PropertyEvaluationContext] = None) -> Any:
        """Get the value of a property of the container item.

        :param key: The key of the item to retrieve a property from.
        :param property_name: The name of the property to retrieve.
        :return: The specified property value of the container item corresponding to key, or None if not found.
        """

        pass

    def hasProperty(self, key: str, property_name: str) -> bool:
        """Get whether the container item has a specific property.

        :param key: The key of the item to check the property from.
        :param name: The name of the property to check for.

        :return: True if the specified item has the property, or False if it
        doesn't.
        """

        pass

    def getAllKeys(self) -> Set[str]:
        """Get all the setting keys known to this container.

        :return: Set of keys.
        """

        pass

    def serialize(self, ignored_metadata_keys: Optional[Set[str]] = None) -> str:
        """Serialize this container to a string.

        The serialized representation of the container can be used to write the
        container to disk or send it over the network.

        :param ignored_metadata_keys: A set of keys that should be ignored when
        it serializes the metadata.

        :return: A string representation of this container.
        """

        pass

    def setProperty(self, key: str, property_name: str, property_value: Any, container: "ContainerInterface" = None, set_from_cache: bool = False) -> None:
        """Change a property of a container item.

        :param key: The key of the item to change the property of.
        :param property_name: The name of the property to change.
        :param property_value: The new value of the property.
        :param container: The container to use for retrieving values when
        changing the property triggers property updates. Defaults to None, which
        means use the current container.
        :param set_from_cache: Flag to indicate that the property was set from
        cache. This triggers the behavior that the read_only and setDirty are
        ignored.
        """

        pass

    # Should return false (or even throw an exception) if trust (or other verification) is invalidated.
    def _trustHook(self, file_name: Optional[str]) -> bool:
        return True

    def deserialize(self, serialized: str, file_name: Optional[str] = None) -> str:
        """Deserialize the container from a string representation.

        This should replace the contents of this container with those in the serialized
        representation.

        :param serialized: A serialized string containing a container that should be deserialized.
        """

        if not self._trustHook(file_name):
            return ""
        return self._updateSerialized(serialized, file_name = file_name)

    @classmethod
    def deserializeMetadata(cls, serialized: str, container_id: str) -> List[Dict[str, Any]]:
        """Deserialize just the metadata from a string representation.

        :param serialized: A string representing one or more containers that
        should be deserialized.
        :param container_id: The ID of the (base) container is already known and
        provided here.

        :return: A list of the metadata of all containers found in the document.
        """

        Logger.log("w", "Class {class_name} hasn't implemented deserializeMetadata!".format(class_name = cls.__name__))
        return []

    @classmethod
    def _updateSerialized(cls, serialized: str, file_name: Optional[str] = None) -> str:
        """Updates the given serialized data to the latest version."""

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

    @classmethod
    def getConfigurationTypeFromSerialized(cls, serialized: str) -> Optional[str]:
        """Gets the configuration type of the given serialized data. (used by __updateSerialized())"""

        pass

    @classmethod
    def getVersionFromSerialized(cls, serialized: str) -> Optional[int]:
        """Gets the version of the given serialized data. (used by __updateSerialized())"""

        pass

    def getPath(self) -> str:
        """Get the path used to create this InstanceContainer."""

        pass

    def setPath(self, path: str) -> None:
        """Set the path used to create this InstanceContainer"""

        pass

    def isDirty(self) -> bool:
        pass

    def setDirty(self, dirty: bool) -> None:
        pass

    propertyChanged = None   # type: Signal

    metaDataChanged = None  # type: Signal


@UM.Decorators.interface
class DefinitionContainerInterface(ContainerInterface):
    def findDefinitions(self, **kwargs: Any) -> List["SettingDefinition"]:
        raise NotImplementedError()

    def setProperty(self, key: str, property_name: str, property_value: Any, container: "ContainerInterface" = None, set_from_cache: bool = False) -> None:
        raise TypeError("Can't change properties in definition containers.")

    def getInheritedFiles(self) -> List[str]:
        raise NotImplementedError()


@UM.Decorators.interface
class ContainerRegistryInterface:
    """Shared interface between setting container types"""

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

    def setExplicitReadOnly(self, container_id: str) -> None:
        raise NotImplementedError()

    def isExplicitReadOnly(self, container_id: str) -> bool:
        raise NotImplementedError()
