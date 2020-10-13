# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser
import io
import copy
import os
from typing import Any, cast, Dict, List, Optional, Set, Tuple

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QQmlEngine #To take ownership of this class ourselves.

from UM.FastConfigParser import FastConfigParser
from UM.Trust import Trust
from UM.Decorators import override
from UM.Settings.Interfaces import DefinitionContainerInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext #For typing.
from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType

from UM.Settings.Interfaces import ContainerInterface, ContainerRegistryInterface
from UM.Settings.SettingInstance import SettingInstance
import re

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


@signalemitter
class InstanceContainer(QObject, ContainerInterface, PluginObject):
    """A container for SettingInstance objects."""

    Version = 4
    version_regex = re.compile("\nversion ?= ?(\d+)")
    setting_version_regex = re.compile("\nsetting_version ?= ?(\d+)")
    type_regex = re.compile("\ntype ?= ?(\w+)")

    def __init__(self, container_id: str, parent: QObject = None, *args: Any, **kwargs: Any) -> None:
        """Constructor

        :param container_id: A unique, machine readable/writable ID for this container.
        """

        super().__init__()
        QQmlEngine.setObjectOwnership(self, QQmlEngine.CppOwnership)

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
        self._postponed_emits = []  # type: List[Tuple[Signal, Tuple[str, str]]]
        self._definition = None  # type: Optional[DefinitionContainerInterface]

        self._cached_values = None  # type: Optional[Dict[str, Any]]

    def __hash__(self) -> int:
        # We need to re-implement the hash, because we defined the __eq__ operator.
        # According to some, returning the ID is technically not right, as objects with the same value should return
        # the same hash. The way we use it, it is acceptable for objects with the same value to return a different hash.
        return id(self)

    def __deepcopy__(self, memo: Dict[int, object]) -> "InstanceContainer":
        new_container = self.__class__(self.getId())
        new_container._metadata = cast(Dict[str, Any], copy.deepcopy(self._metadata, memo))
        new_container._instances = cast(Dict[str, SettingInstance], copy.deepcopy(self._instances, memo))
        for instance in new_container._instances.values(): #Set the back-links of the new instances correctly to the copied container.
            instance._container = new_container
            instance.propertyChanged.connect(new_container.propertyChanged)
        new_container._read_only = self._read_only
        new_container._dirty = self._dirty
        new_container._path = cast(str, copy.deepcopy(self._path, memo))
        new_container._cached_values = cast(Optional[Dict[str, Any]], copy.deepcopy(self._cached_values, memo))
        return new_container

    def __eq__(self, other: object) -> bool:
        if type(self) != type(other):
            return False  # Type mismatch
        other = cast(InstanceContainer, other)

        self._instantiateCachedValues()
        other._instantiateCachedValues()
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

    def __getnewargs__(self) -> Tuple[str]:
        """For pickle support"""

        return (self.getId(),)

    def __getstate__(self) -> Dict[str, Any]:
        """For pickle support"""

        return self.__dict__

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """For pickle support"""

        self.__dict__.update(state)

    def getId(self) -> str:
        """:copydoc ContainerInterface::getId

        Reimplemented from ContainerInterface
        """

        return self._metadata["id"]

    id = pyqtProperty(str, fget = getId, constant = True)

    def setCachedValues(self, cached_values: Dict[str, Any]) -> None:
        if not self._instances:
            self._cached_values = cached_values
        else:
            Logger.log("w", "Unable set values to be lazy loaded when values are already loaded ")

    @classmethod
    def getLoadingPriority(cls) -> int:
        return 1

    def getPath(self) -> str:
        """:copydoc ContainerInterface::getPath.

        Reimplemented from ContainerInterface
        """

        return self._path

    def setPath(self, path: str) -> None:
        """:copydoc ContainerInterface::setPath

        Reimplemented from ContainerInterface
        """

        self._path = path

    def getName(self) -> str:
        """:copydoc ContainerInterface::getName

        Reimplemented from ContainerInterface
        """

        return self._metadata["name"]

    def setName(self, name: str) -> None:
        if name != self.getName():
            self._metadata["name"] = name
            self._dirty = True
            self.nameChanged.emit()
            self.pyqtNameChanged.emit()
            self.metaDataChanged.emit(self)


    # Because we want to expose the properties of InstanceContainer as Qt properties for
    # CURA-3497, the nameChanged signal should be changed to a pyqtSignal. However,
    # pyqtSignal throws TypeError when calling disconnect() when there are no connections.
    # This causes a lot of errors in Cura code when we try to disconnect from nameChanged.
    # Therefore, rather than change the type of nameChanged, we add an extra signal that
    # is used as notify for the property.
    #
    # TODO: Remove this once the Cura code has been refactored to not use nameChanged anymore.
    pyqtNameChanged = pyqtSignal()

    nameChanged = Signal()
    name = pyqtProperty(str, fget = getName, fset = setName, notify = pyqtNameChanged)

    def getReadOnly(self) -> bool:
        return _containerRegistry.isReadOnly(self.getId())  # TODO???: Why not also take self._read_only into account?
    readOnly = pyqtProperty(bool, fget = getReadOnly)

    def getNumInstances(self) -> int:
        return len(self._instances)

    def getMetaData(self) -> Dict[str, Any]:
        """:copydoc ContainerInterface::getMetaData

        Reimplemented from ContainerInterface
        """

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
            "version": self.getMetaData().get("version", 0),
            "container_type": InstanceContainer
        }
        self._metadata.update(metadata)
        self._dirty = True
        self.metaDataChanged.emit(self)

    metaDataChanged = pyqtSignal(QObject)
    metaData = pyqtProperty("QVariantMap", fget = getMetaData, fset = setMetaData, notify = metaDataChanged)

    def getMetaDataEntry(self, entry: str, default = None) -> Any:
        """:copydoc ContainerInterface::getMetaDataEntry

        Reimplemented from ContainerInterface
        """

        return self._metadata.get(entry, default)

    def setMetaDataEntry(self, key: str, value: Any) -> None:
        """Set a metadata entry to a certain value.

        :param key: The key of the metadata entry to set.
        :param value: The new value of the metadata.

        :note This does nothing if the key is not already added to the metadata.
        """

        if key not in self._metadata or self._metadata[key] != value:
            self._metadata[key] = value
            self._dirty = True
            self.metaDataChanged.emit(self)

    def isDirty(self) -> bool:
        """Check if this container is dirty, that is, if it changed from deserialization."""

        return self._dirty

    def setDirty(self, dirty: bool) -> None:
        if self._read_only:
            Logger.log("w", "Tried to set dirty on read-only object.")
        else:
            self._dirty = dirty

    def getProperty(self, key: str, property_name: str, context: PropertyEvaluationContext = None) -> Any:
        """:copydoc ContainerInterface::getProperty

        Reimplemented from ContainerInterface
        """

        # Instance containers can only set value, state & validationstate, so if someone asks for anything else, quit early.
        if property_name not in ["value", "state", "validationState"]:
            return None
        self._instantiateCachedValues()
        if key in self._instances:
            try:
                return getattr(self._instances[key], property_name)
            except AttributeError:
                pass

        return None

    def hasProperty(self, key: str, property_name: str) -> bool:
        """:copydoc ContainerInterface::hasProperty

        Reimplemented from ContainerInterface.
        """

        # --- Kinda a hack:
        # When we check if a property exists, it is not necessary to flush the cache because we simply want to know
        # whether it is there. Flushing the cache can cause propertyChanged signals being emitted, and, as a result,
        # may cause undesired behaviours.
        #
        # So, in this case, we only instantiate the missing setting instances that are present in the cache (if any)
        # **WITHOUT** applying the cached values. This way there won't be any property changed signals when we are
        # just checking if a property exists.
        #
        if self._cached_values and key in self._cached_values and property_name == "value":
            return True
        self._instantiateMissingSettingInstancesInCache()
        return key in self._instances and hasattr(self._instances[key], property_name)

    def _instantiateMissingSettingInstancesInCache(self) -> None:
        """Creates SettingInstances that are missing in this InstanceContainer from the cache if any.
        This function will **ONLY instantiate SettingInstances. The cached values will not be applied.**
        """

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
                instance.propertyChanged.connect(self.propertyChanged)
                self._instances[instance.definition.key] = instance

    def setProperty(self, key: str, property_name: str, property_value: Any, container: ContainerInterface = None, set_from_cache: bool = False) -> None:
        """Set the value of a property of a SettingInstance.

        This will set the value of the specified property on the SettingInstance corresponding to key.
        If no instance has been created for the specified key, a new one will be created and inserted
        into this instance.

        :param key: The key of the setting to set a property of.
        :param property_name:  The name of the property to set.
        :param property_value: The new value of the property.
        :param container: The container to use for retrieving values when changing the property triggers property
        updates. Defaults to None, which means use the current container.
        :param set_from_cache: Flag to indicate that the property was set from cache. This triggers the behavior that
        the read_only and setDirty are ignored.

        :note If no definition container is set for this container, new instances cannot be created and this method
        will do nothing.
        """

        if self._read_only and not set_from_cache:
            Logger.log(
                "w",
                "Tried to setProperty [%s] with value [%s] with key [%s] on read-only object [%s]" % (
                    property_name, property_value, key, self.id))
            return

        if key not in self._instances:
            try:
                definition = self.getDefinition()
            except DefinitionNotFoundError:
                Logger.log("w", "Tried to set value of setting when the container has no definition")
                return
            setting_definition = definition.findDefinitions(key = key)
            if not setting_definition:
                Logger.log("w", "Tried to set value of setting %s that has no instance in container %s or its definition %s", key, self.getName(), self.getDefinition().getName())
                return

            instance = SettingInstance(setting_definition[0], self)
            instance.propertyChanged.connect(self.propertyChanged)
            self._instances[instance.definition.key] = instance

        # Do not emit any signal if the value is set from cache
        self._instances[key].setProperty(property_name, property_value, container, emit_signals = not set_from_cache)

        if not set_from_cache:
            self.setDirty(True)

    propertyChanged = Signal()

    def clear(self) -> None:
        """Remove all instances from this container."""

        self._instantiateCachedValues()
        all_keys = self._instances.copy()
        for key in all_keys:
            self.removeInstance(key, postpone_emit=True)
        self.sendPostponedEmits()

    def getAllKeys(self) -> Set[str]:
        """Get all the keys of the instances of this container
        :returns: list of keys
        """

        keys = set(key for key in self._instances)
        if self._cached_values:
            # If we only want the keys and the actual values are still cached, just get the keys from the cache.
            keys.update(self._cached_values.keys())
        return keys

    def duplicate(self, new_id: str, new_name: str = None) -> "InstanceContainer":
        """Create a new InstanceContainer with the same contents as this container

        :param new_id: The new ID of the container
        :param new_name: The new name of the container. Defaults to None to indicate the name should not change.

        :return: A new InstanceContainer with the same contents as this container.
        """

        self._instantiateCachedValues()
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

    def serialize(self, ignored_metadata_keys: Optional[Set[str]] = None) -> str:
        """:copydoc ContainerInterface::serialize

        Reimplemented from ContainerInterface
        """

        self._instantiateCachedValues()
        parser = configparser.ConfigParser(interpolation = None)

        try:
            self.getDefinition()
        except DefinitionNotFoundError:
            Logger.log("w", "Tried to serialize an instance container without definition, this is not supported")
            return ""

        parser["general"] = {}
        parser["general"]["version"] = str(self.Version)
        parser["general"]["name"] = str(self.getName())
        parser["general"]["definition"] = str(self.getDefinition().getId())

        if ignored_metadata_keys is None:
            ignored_metadata_keys = set()
        else:
            ignored_metadata_keys = ignored_metadata_keys.copy() #Don't modify the input set.
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

    @classmethod
    def _readAndValidateSerialized(cls, serialized: str) -> FastConfigParser:
        # Disable comments in the ini files, so text values can start with a ;
        # without being removed as a comment
        parser = FastConfigParser(serialized)

        has_general = "general" in parser
        has_version = has_general and "version" in parser["general"]
        has_definition = has_general and "definition" in parser["general"]

        if not has_general or not has_version or not has_definition:
            exception_string = "Missing the required"
            if not has_general:
                exception_string += " section 'general'"
            if not has_definition:
                exception_string += " property 'definition'"
            if not has_version:
                exception_string += " property 'version'"
            raise InvalidInstanceError(exception_string)
        return parser

    @classmethod
    def getConfigurationTypeFromSerialized(cls, serialized: str) -> Optional[str]:
        regex_result = cls.type_regex.search(serialized)
        configuration_type = ""
        if regex_result is not None:
            configuration_type = str(regex_result.groups()[-1])

        return configuration_type

    @classmethod
    def getVersionFromSerialized(cls, serialised: str) -> int:
        """
        Gets the version number from a config file.

        In all config files that concern this version upgrade, the version number is stored in general/version, so get
        the data from that key.

        :param serialised: The contents of a config file.
        :return: The version number of that config file.
        """
        format_version = 1
        setting_version = 0

        regex_result = cls.version_regex.search(serialised)
        if regex_result is not None:
            format_version = int(regex_result.groups()[-1])

        regex_result = cls.setting_version_regex.search(serialised)
        if regex_result is not None:
            setting_version = int(regex_result.groups()[-1])

        return format_version * 1000000 + setting_version

    @override(ContainerInterface)
    def _trustHook(self, file_name: Optional[str]) -> bool:
        # NOTE: In an enterprise environment, if there _is_ a signature file for an unbundled package, verify it.
        #       (Note that this is a different behaviour w.r.t. the plugins, where the check is not just verification!)
        #       (Note that there shouldn't be a check if trust has to be here, since it'll continue on 'no signature'.)
        if file_name is None:
            return True
        trust_instance = Trust.getInstanceOrNone()
        if trust_instance is not None:
            from UM.Application import Application
            install_prefix = os.path.abspath(Application.getInstallPrefix())
            try:
                common_path = os.path.commonpath([install_prefix, file_name])
            except ValueError:
                common_path = ""
            if common_path == "" or not common_path.startswith(install_prefix):
                if trust_instance.signatureFileExistsFor(file_name):
                    _containerRegistry.setExplicitReadOnly(self.getId())  # TODO???: self._read_only = True
                    if not trust_instance.signedFileCheck(file_name):
                        raise Exception("Can't validate file {0}".format(file_name))
        return True

    def deserialize(self, serialized: str, file_name: Optional[str] = None) -> str:
        """:copydoc ContainerInterface::deserialize

        Reimplemented from ContainerInterface
        """

        # update the serialized data first
        serialized = super().deserialize(serialized, file_name)
        parser = self._readAndValidateSerialized(serialized)

        try:
            parser_version = int(parser["general"]["version"])
        except ValueError:  # Version number is not integer.
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
        self.metaDataChanged.emit(self) #In case this instance was re-used.

        if "values" in parser:
            self._cached_values = dict(parser["values"])

        self._dirty = False

        return serialized

    @classmethod
    def deserializeMetadata(cls, serialized: str, container_id: str) -> List[Dict[str, Any]]:
        """Gets the metadata of an instance container from a serialised format.

        This parses the entire CFG document and only extracts the metadata from
        it.

        :param serialized: A CFG document, serialised as a string.
        :param container_id: The ID of the container to get the metadata of, as obtained from the file name.
        :return: A dictionary of metadata that was in the CFG document in a singleton list. If anything went
        wrong, this returns an empty list instead.
        """

        serialized = cls._updateSerialized(serialized)  # Update to most recent version.
        parser = FastConfigParser(serialized)

        metadata = {
            "id": container_id,
            "container_type": InstanceContainer
        }
        try:
            metadata["name"] = parser["general"]["name"]
            metadata["version"] = parser["general"]["version"]
            metadata["definition"] = parser["general"]["definition"]
        except KeyError as e: #One of the keys or the General section itself is missing.
            raise InvalidInstanceError("Missing required fields: {error_msg}".format(error_msg = str(e)))

        if "metadata" in parser:
            metadata = {**metadata, **parser["metadata"]}

        return [metadata]

    def _instantiateCachedValues(self) -> None:
        """Instance containers are lazy loaded. This function ensures that it happened."""

        if not self._cached_values:
            return
        definition = self.getDefinition()
        for key, value in self._cached_values.items():
            self.setProperty(key, "value", value, definition, set_from_cache=True)

        self._cached_values = None

    def findInstances(self, **kwargs: Any) -> List[SettingInstance]:
        """Find instances matching certain criteria.

        :param kwargs: A dictionary of keyword arguments with key-value pairs that should match properties of the instances.
        """

        self._instantiateCachedValues()
        result = []
        for setting_key, instance in self._instances.items():
            for key, value in kwargs.items():
                if not hasattr(instance, key) or getattr(instance, key) != value:
                    break
            else:
                result.append(instance)

        return result

    def getInstance(self, key: str) -> Optional[SettingInstance]:
        """Get an instance by key"""

        self._instantiateCachedValues()
        if key in self._instances:
            return self._instances[key]

        return None

    def addInstance(self, instance: SettingInstance) -> None:
        """Add a new instance to this container."""

        self._instantiateCachedValues()
        key = instance.definition.key
        if key in self._instances:
            return

        instance.propertyChanged.connect(self.propertyChanged)
        instance.propertyChanged.emit(key, "value")
        self._instances[key] = instance

    def removeInstance(self, key: str, postpone_emit: bool = False) -> None:
        """Remove an instance from this container.

        :param postpone_emit: postpone emit until calling sendPostponedEmits
        """

        self._instantiateCachedValues()
        if key not in self._instances:
            return

        instance = self._instances[key]
        del self._instances[key]
        if postpone_emit:
            # postpone, call sendPostponedEmits later. The order matters.
            self._postponed_emits.append((instance.propertyChanged, (key, "validationState")))
            self._postponed_emits.append((instance.propertyChanged, (key, "state")))
            self._postponed_emits.append((instance.propertyChanged, (key, "value")))
            for property_name in instance.definition.getPropertyNames():
                if instance.definition.dependsOnProperty(property_name) == "value":
                    self._postponed_emits.append((instance.propertyChanged, (key, property_name)))
        else:
            # Notify listeners of changed properties for all related properties
            instance.propertyChanged.emit(key, "value")
            instance.propertyChanged.emit(key, "state")  # State is no longer user state, so signal is needed.
            instance.propertyChanged.emit(key, "validationState") # If the value was invalid, it should now no longer be invalid.
            for property_name in instance.definition.getPropertyNames():
                if instance.definition.dependsOnProperty(property_name) == "value":
                    self.propertyChanged.emit(key, property_name)

        self._dirty = True

        instance.updateRelations(self)

    def update(self) -> None:
        """Update all instances from this container."""

        self._instantiateCachedValues()
        for key, instance in self._instances.items():
            instance.propertyChanged.emit(key, "value")
            instance.propertyChanged.emit(key, "state")  # State is no longer user state, so signal is needed.
            instance.propertyChanged.emit(key, "validationState")  # If the value was invalid, it should now no longer be invalid.
            for property_name in instance.definition.getPropertyNames():
                if instance.definition.dependsOnProperty(property_name) == "value":
                    self.propertyChanged.emit(key, property_name)
        self._dirty = True

    def getDefinition(self) -> DefinitionContainerInterface:
        """Get the DefinitionContainer used for new instance creation."""

        if self._definition is None:
            definitions = _containerRegistry.findDefinitionContainers(id = self._metadata.get("definition", ""))
            if not definitions:
                raise DefinitionNotFoundError("Could not find definition {0} required for instance {1}".format(self._metadata.get("definition", ""), self.getId()))
            self._definition = definitions[0]
        return self._definition

    def setDefinition(self, definition_id: str) -> None:
        """Set the DefinitionContainer to use for new instance creation.

        Since SettingInstance needs a SettingDefinition to work properly, we need some
        way of figuring out what SettingDefinition to use when creating a new SettingInstance.
        """

        self._metadata["definition"] = definition_id
        self._definition = None

    def __lt__(self, other: object) -> bool:
        if type(other) != type(self):
            return True
        other = cast(InstanceContainer, other)
        own_weight = int(self.getMetaDataEntry("weight", 0))
        other_weight = int(other.getMetaDataEntry("weight", 0))
        if own_weight and other_weight:
            return own_weight < other_weight

        return self.getName() < other.getName()

    def __str__(self) -> str:
        """Simple string representation for debugging."""
        return "<InstContainer '{container_id}'>".format(container_id = self.getId())

    def __repr__(self) -> str:
        return str(self)

    def sendPostponedEmits(self) -> None:
        """Send the postponed emits

        These emits are collected from the option postpone_emit.
        Note: the option can be implemented for all functions modifying the container.
        """

        while self._postponed_emits:
            signal, signal_arg = self._postponed_emits.pop(0)
            signal.emit(*signal_arg)


_containerRegistry = ContainerRegistryInterface()  # type:  ContainerRegistryInterface


def setContainerRegistry(registry: ContainerRegistryInterface) -> None:
    global _containerRegistry
    _containerRegistry = registry
