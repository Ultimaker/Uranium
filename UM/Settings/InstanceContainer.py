# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser
import io
import copy
from typing import Any, cast, Dict, List, Optional, Set, Tuple

from UM.Logging.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType
from UM.Settings.Interfaces import DefinitionContainerInterface, ContainerInterface, ContainerRegistryInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext
from UM.Settings.SettingInstance import SettingInstance


class InvalidInstanceError(Exception):
    pass


class IncorrectInstanceVersionError(Exception):
    pass


class DefinitionNotFoundError(Exception):
    pass


MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-instancecontainer",
        comment = "Uranium Instance Container",
        suffixes = [ "inst.cfg" ]
    )
)


##  A container for SettingInstance objects.
#
class InstanceContainer(ContainerInterface):
    Version = 4

    def __init__(self, container_id: str, *args: Any, **kwargs: Any) -> None:
        super().__init__()

        self._metadata = {
            "id": container_id,
            "name": container_id,
            "version": self.Version,
            "container_type": InstanceContainer
        }                               # type: Dict[str, Any]
        self._instances = {}            # type: Dict[str, SettingInstance]
        self._read_only = False  # type: bool
        self._dirty = False  # type: bool
        self._path = ""  # type: str

        self._cached_values = None  # type: Optional[Dict[str, Any]]

    def __hash__(self) -> int:
        # We need to re-implement the hash, because we defined the __eq__ operator.
        # According to some, returning the ID is technically not right, as objects with the same value should return
        # the same hash. The way we use it, it is acceptable for objects with the same value to return a different hash.
        return id(self)

    def __deepcopy__(self, memo: Dict[int, object]) -> "InstanceContainer":
        new_container = self.__class__(self.getId())
        new_container._metadata = copy.deepcopy(self._metadata, memo)
        new_container._instances = cast(Dict[str, SettingInstance], copy.deepcopy(self._instances, memo))
        for instance in new_container._instances.values(): #Set the back-links of the new instances correctly to the copied container.
            instance._container = new_container
        new_container._read_only = self._read_only
        new_container._dirty = self._dirty
        new_container._path = copy.deepcopy(self._path, memo)
        return new_container

    def __eq__(self, other: object) -> bool:
        if type(self) != type(other):
            return False  # Type mismatch
        other = cast(InstanceContainer, other)

        if self.getId() != other.getId():
            return False  # ID mismatch

        for entry in self._metadata:
            if other.getMetaDataEntry(entry) != self._metadata[entry]:
                return False  # Meta data entry mismatch

        for entry in other.getMetaData():
            if entry not in self._metadata:
                return False  # Other has a meta data entry that this object does not have.

        for key in self._instances:
            if key not in other._instances:
                return False  # This object has an instance that other does not have.
            if self._instances[key] != other._instances[key]:
                return False  # The objects don't match.

        for key in other._instances:
            if key not in self._instances:
                return False  # Other has an instance that this object does not have.
        return True

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    ##  For pickle support
    def __getnewargs__(self) -> Tuple[str]:
        return (self.getId(),)

    ##  For pickle support
    def __getstate__(self) -> Dict[str, Any]:
        return self.__dict__

    ##  For pickle support
    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self) -> str:
        return self._metadata["id"]

    def setCachedValues(self, cached_values: Dict[str, Any]) -> None:
        if not self._instances:
            self._cached_values = cached_values
        else:
            Logger.log("w", "Unable set values to be lazy loaded when values are already loaded ")

    @classmethod
    def getLoadingPriority(cls) -> int:
        return 1

    ##  \copydoc ContainerInterface::getPath.
    #
    #   Reimplemented from ContainerInterface
    def getPath(self) -> str:
        return self._path

    ##  \copydoc ContainerInterface::setPath
    #
    #   Reimplemented from ContainerInterface
    def setPath(self, path: str) -> None:
        self._path = path

    ##  \copydoc ContainerInterface::getName
    #
    #   Reimplemented from ContainerInterface
    def getName(self) -> str:
        return self._metadata["name"]

    def setName(self, name: str) -> None:
        if name != self.getName():
            self._metadata["name"] = name
            self._dirty = True

    # Because we want to expose the properties of InstanceContainer as Qt properties for
    # CURA-3497, the nameChanged signal should be changed to a pyqtSignal. However,
    # pyqtSignal throws TypeError when calling disconnect() when there are no connections.
    # This causes a lot of errors in Cura code when we try to disconnect from nameChanged.
    # Therefore, rather than change the type of nameChanged, we add an extra signal that
    # is used as notify for the property.
    #
    def getReadOnly(self) -> bool:
        return _containerRegistry.isReadOnly(self.getId())

    ##  \copydoc ContainerInterface::getMetaData
    #
    #   Reimplemented from ContainerInterface
    def getMetaData(self) -> Dict[str, Any]:
        return self._metadata

    def setMetaData(self, metadata: Dict[str, Any]) -> None:
        if metadata == self._metadata:
            return #No need to do anything or even emit the signal.

        #We'll fill a temporary dictionary with all the required metadata and overwrite it with the new metadata.
        #This way it is ensured that at least the required metadata is still there.
        self._metadata = {
            "id": self.getId(),
            "name": self.getName(),
            "definition": self.getMetaData().get("definition"),
            "version": self.getMetaData().get("version", 0)
        }
        self._metadata.update(metadata)
        self._dirty = True

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry: str, default = None) -> Any:
        return self._metadata.get(entry, default)

    ##  Add a new entry to the metadata of this container.
    #
    #   \param key \type{str} The key of the new entry.
    #   \param value The value of the new entry.
    #
    #   \note This does nothing if the key already exists.
    def addMetaDataEntry(self, key: str, value: Any) -> None:
        if key not in self._metadata:
            self._metadata[key] = value
            self._dirty = True
        else:
            Logger.log("w", "Meta data with key %s was already added.", key)

    ##  Set a metadata entry to a certain value.
    #
    #   \param key The key of the metadata entry to set.
    #   \param value The new value of the metadata.
    #
    #   \note This does nothing if the key is not already added to the metadata.
    def setMetaDataEntry(self, key: str, value: Any) -> None:
        if self._metadata.get(key) != value:
            self._dirty = True
        self._metadata[key] = value

    ##  Check if this container is dirty, that is, if it changed from deserialization.
    def isDirty(self) -> bool:
        return self._dirty

    def setDirty(self, dirty: bool) -> None:
        if self._read_only:
            Logger.log("w", "Tried to set dirty on read-only object.")
        else:
            self._dirty = dirty

    ##  \copydoc ContainerInterface::getProperty
    #
    #   Reimplemented from ContainerInterface
    def getProperty(self, key: str, property_name: str, context: PropertyEvaluationContext = None) -> Any:
        if key in self._instances:
            try:
                return getattr(self._instances[key], property_name)
            except AttributeError:
                pass

        return None

    ##  \copydoc ContainerInterface::hasProperty
    #
    #   Reimplemented from ContainerInterface.
    def hasProperty(self, key: str, property_name: str) -> bool:
        # --- Kinda a hack:
        # When we check if a property exists, it is not necessary to flush the cache because we simply want to know
        # whether it is there. Flushing the cache can cause propertyChanged signals being emitted, and, as a result,
        # may cause undesired behaviours.
        #
        # So, in this case, we only instantiate the missing setting instances that are present in the cache (if any)
        # **WITHOUT** applying the cached values. This way there won't be any property changed signals when we are
        # just checking if a property exists.
        #
        self._instantiateMissingSettingInstancesInCache()
        if self._cached_values and key in self._cached_values and property_name == "value":
            return True
        return key in self._instances and hasattr(self._instances[key], property_name)

    ##  Creates SettingInstances that are missing in this InstanceContainer from the cache if any.
    #   This function will **ONLY instantiate SettingInstances. The cached values will not be applied.**
    def _instantiateMissingSettingInstancesInCache(self) -> None:
        if not self._cached_values:
            return

        for key, value in self._cached_values.items():
            if key not in self._instances:
                if not self.getDefinition():
                    Logger.log("w", "Tried to set value of setting %s that has no instance in container %s and the container has no definition", key, self.getName())
                    return

                setting_definition = self.getDefinition().findDefinitions(key = key)
                if not setting_definition:
                    Logger.log("w", "Tried to set value of setting %s that has no instance in container %s or its definition %s", key, self.getName(), self.getDefinition().getName())
                    return

                instance = SettingInstance(setting_definition[0], self)
                self._instances[instance.definition.key] = instance

    def setProperty(self, key: str, property_name: str, property_value: Any) -> None:
        if self._read_only:
            Logger.log(
                "w",
                "Tried to setProperty [%s] with value [%s] with key [%s] on read-only object [%s]" % (
                    property_name, property_value, key, self.getId()))
            return
        if key not in self._instances:
            if not self.getDefinition():
                Logger.log("w", "Tried to set value of setting %s that has no instance in container %s and the container has no definition", key, self.getName())
                return

            setting_definition = self.getDefinition().findDefinitions(key = key)
            if not setting_definition:
                Logger.log("w", "Tried to set value of setting %s that has no instance in container %s or its definition %s", key, self.getName(), self.getDefinition().getName())
                return

            instance = SettingInstance(setting_definition[0], self)
            self._instances[instance.definition.key] = instance

        # Do not emit any signal if the value is set from cache
        self._instances[key].setProperty(property_name, property_value)

        self._dirty = True

    def clear(self) -> None:
        all_keys = self._instances.copy()
        for key in all_keys:
            self.removeInstance(key)

    def getAllKeys(self) -> Set[str]:
        keys = set(key for key in self._instances)
        return keys

    def duplicate(self, new_id: str, new_name: str = None) -> "InstanceContainer":
        new_container = self.__class__(new_id)
        new_metadata = copy.deepcopy(self._metadata)
        if new_name:
            new_container.setName(new_name)
        else:
            new_container.setName(new_metadata.get("name", ""))

        for key_to_remove in ["id", "name"]:
            if key_to_remove in new_metadata:
                del new_metadata[key_to_remove]
        new_container.setMetaData(new_metadata)

        for instance_id in self._instances:
            instance = self._instances[instance_id]
            for property_name in instance.definition.getPropertyNames():
                if not hasattr(instance, property_name):
                    continue

                new_container.setProperty(instance.definition.key, property_name, getattr(instance, property_name))

        new_container._dirty = True
        new_container._read_only = False
        return new_container

    def serialize(self, ignored_metadata_keys: Optional[set] = None) -> str:
        parser = configparser.ConfigParser(interpolation = None)

        if not self.getDefinition():
            Logger.log("w", "Tried to serialize an instance container without definition, this is not supported")
            return ""

        parser["general"] = {}
        parser["general"]["version"] = str(self.Version)
        parser["general"]["name"] = str(self.getName())
        parser["general"]["definition"] = str(self.getDefinition().getId())

        if ignored_metadata_keys is None:
            ignored_metadata_keys = set()
        else:
            ignored_metadata_keys = ignored_metadata_keys.copy()  # Don't modify the input set.
        ignored_metadata_keys |= {"id", "version", "name", "container_type", "definition"}
        parser["metadata"] = {}
        for key, value in self._metadata.items():
            if key not in ignored_metadata_keys:
                parser["metadata"][key] = str(value)

        parser["values"] = {}
        for key, instance in sorted(self._instances.items()):
            try:
                parser["values"][key] = str(instance.value)
            except AttributeError:
                pass

        stream = io.StringIO()
        parser.write(stream)
        return stream.getvalue()

    def deserialize(self, serialized: str, file_name: Optional[str] = None) -> str:
        parser = configparser.ConfigParser(interpolation = None)
        parser.read_string(serialized)

        try:
            parser_version = int(parser["general"]["version"])
        except ValueError:
            raise IncorrectInstanceVersionError("Reported version {0} is not an integer.".format(parser["general"]["version"]))
        if parser_version != self.Version:
            raise IncorrectInstanceVersionError("Reported version {0} but expected version {1}".format(str(parser_version), self.Version))

        # Reset old data
        old_id = self.getId()
        self._metadata = {}
        self._instances = {}

        if "metadata" in parser:
            self._metadata = dict(parser["metadata"])
        self._metadata["id"] = old_id
        self._metadata["name"] = parser["general"].get("name", self.getId())
        self._metadata["container_type"] = InstanceContainer
        self._metadata["version"] = parser_version
        self._metadata["definition"] = parser["general"]["definition"]

        if "values" in parser:
            for key, value in parser["values"].items():
                self.setProperty(key, "value", value)

        self._dirty = False

        return serialized

    @classmethod
    def deserializeMetadata(cls, serialized: str, container_id: str) -> List[Dict[str, Any]]:
        parser = configparser.ConfigParser(interpolation = None)
        parser.read_string(serialized)

        metadata = {
            "id": container_id,
            "container_type": InstanceContainer
        }
        try:
            metadata["name"] = parser["general"]["name"]
            metadata["version"] = parser["general"]["version"]
            metadata["definition"] = parser["general"]["definition"]
        except KeyError as e:  # One of the keys or the General section itself is missing.
            raise InvalidInstanceError("Missing required fields: {error_msg}".format(error_msg = str(e)))

        if "metadata" in parser:
            metadata = {**metadata, **parser["metadata"]}

        return [metadata]

    def findInstances(self, **kwargs: Any) -> List[SettingInstance]:
        result = []
        for setting_key, instance in self._instances.items():
            for key, value in kwargs.items():
                if not hasattr(instance, key) or getattr(instance, key) != value:
                    break
            else:
                result.append(instance)

        return result

    def getInstance(self, key: str) -> Optional[SettingInstance]:
        return self._instances.get(key)

    def addInstance(self, instance: SettingInstance) -> None:
        key = instance.definition.key
        if key not in self._instances:
            self._instances[key] = instance
        self._dirty = True

    def removeInstance(self, key: str) -> None:
        if key in self._instances:
            return

        del self._instances[key]
        self._dirty = True

    def getDefinition(self) -> DefinitionContainerInterface:
        definitions = _containerRegistry.findDefinitionContainers(id = self._metadata["definition"])
        if not definitions:
            raise DefinitionNotFoundError("Could not find definition {0} required for instance {1}".format(self._metadata["definition"], self.getId()))
        return definitions[0]

    def setDefinition(self, definition_id: str) -> None:
        self._metadata["definition"] = definition_id

    def __lt__(self, other: object) -> bool:
        if type(other) != type(self):
            return True
        other = cast(InstanceContainer, other)
        own_weight = int(self.getMetaDataEntry("weight", 0))
        other_weight = int(other.getMetaDataEntry("weight", 0))

        if own_weight and other_weight:
            return own_weight < other_weight

        return self.getName() < other.getName()

    # Simple string representation for debugging.
    def __str__(self) -> str:
        return "<InstanceContainer '{container_id}' ('{name}')>".format(container_id = self.getId(), name = self.getName())


_containerRegistry = ContainerRegistryInterface()   # type:  ContainerRegistryInterface


def setContainerRegistry(registry: ContainerRegistryInterface) -> None:
    global _containerRegistry
    _containerRegistry = registry
