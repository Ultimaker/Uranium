# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import configparser
import io
from typing import Any, cast, Dict, List, Optional, Set

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

import UM.FlameProfiler

from UM.ConfigurationErrorMessage import ConfigurationErrorMessage
from UM.Logger import Logger
from UM.Settings.ContainerFormatError import ContainerFormatError
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType
from UM.Settings.DefinitionContainer import DefinitionContainer #For getting all definitions in this stack.
from UM.Settings.Interfaces import ContainerInterface, ContainerRegistryInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext
from UM.Settings.SettingFunction import SettingFunction
from UM.Settings.Validator import ValidatorState


class IncorrectVersionError(Exception):
    pass


class InvalidContainerStackError(Exception):
    pass

MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-containerstack",
        comment = "Uranium Container Stack",
        suffixes = [ "stack.cfg" ]
    )
)

MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-uranium-extruderstack",
        comment = "Uranium Extruder Stack",
        suffixes = [ "stack.cfg" ]
    )
)


##  A stack of setting containers to handle setting value retrieval.
@signalemitter
class ContainerStack(QObject, ContainerInterface, PluginObject):
    Version = 4 # type: int

    ##  Constructor
    #
    #   \param stack_id \type{string} A unique, machine readable/writable ID.
    def __init__(self, stack_id: str, parent = None, *args, **kwargs):
        # Note that we explicitly pass None as QObject parent here. This is to be able
        # to support pickling.
        super().__init__(parent = parent, *args, **kwargs)

        self._metadata = {
            "id": stack_id,
            "name": stack_id,
            "version": self.Version,
            "container_type": ContainerStack
        }
        self._containers = []  # type: List[ContainerInterface]
        self._next_stack = None  # type: Optional[ContainerStack]
        self._read_only = False  # type: bool
        self._dirty = True  # type: bool
        self._path = ""  # type: str
        self._postponed_emits = []  # gets filled with 2-tuples: signal, signal_argument(s)

        self._property_changes = {}
        self._emit_property_changed_queued = False  # type: bool

    ##  For pickle support
    def __getnewargs__(self):
        return (self.getId(),)

    ##  For pickle support
    def __getstate__(self):
        return self.__dict__

    ##  For pickle support
    def __setstate__(self, state):
        self.__dict__.update(state)

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self) -> str:
        return self._metadata["id"]

    id = pyqtProperty(str, fget = getId, constant = True)

    ##  \copydoc ContainerInterface::getName
    #
    #   Reimplemented from ContainerInterface
    def getName(self) -> str:
        return str(self._metadata["name"])

    ##  Set the name of this stack.
    #
    #   \param name \type{string} The new name of the stack.
    def setName(self, name: str) -> None:
        if name != self.getName():
            self._metadata["name"] = name
            self.nameChanged.emit()
            self.metaDataChanged.emit(self)

    ##  Emitted whenever the name of this stack changes.
    nameChanged = pyqtSignal()
    name = pyqtProperty(str, fget = getName, fset = setName, notify = nameChanged)

    ##  \copydoc ContainerInterface::isReadOnly
    #
    #   Reimplemented from ContainerInterface
    def isReadOnly(self) -> bool:
        return self._read_only

    def setReadOnly(self, read_only):
        if read_only != self._read_only:
            self._read_only = read_only
            self.readOnlyChanged.emit()

    readOnlyChanged = pyqtSignal()
    readOnly = pyqtProperty(bool, fget = isReadOnly, fset = setReadOnly, notify = readOnlyChanged)

    ##  \copydoc ContainerInterface::getMetaData
    #
    #   Reimplemented from ContainerInterface
    def getMetaData(self):
        return self._metadata

    ##  Set the complete set of metadata
    def setMetaData(self, meta_data):
        if meta_data != self._meta_data:
            self._meta_data = meta_data
            self.metaDataChanged.emit(self)

    metaDataChanged = pyqtSignal(QObject)
    metaData = pyqtProperty("QVariantMap", fget = getMetaData, fset = setMetaData, notify = metaDataChanged)

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry: str, default = None):
        value = self._metadata.get(entry, None)

        if value is None:
            for container in self._containers:
                value = container.getMetaDataEntry(entry, None)
                if value is not None:
                    break

        if value is None:
            return default
        else:
            return value

    def addMetaDataEntry(self, key: str, value):
        if key not in self._metadata:
            self._dirty = True
            self._metadata[key] = value
            self.metaDataChanged.emit(self)
        else:
            Logger.log("w", "Meta data with key %s was already added.", key)

    def setMetaDataEntry(self, key, value):
        if key in self._metadata:
            self._dirty = True
            self._metadata[key] = value
            self.metaDataChanged.emit(self)
        else:
            Logger.log("w", "Meta data with key %s was not found. Unable to change.", key)

    def removeMetaDataEntry(self, key):
        if key in self._metadata:
            del self._metadata[key]
            self.metaDataChanged.emit(self)

    def isDirty(self) -> bool:
        return self._dirty

    def setDirty(self, dirty: bool) -> None:
        self._dirty = dirty

    containersChanged = Signal()

    ##  \copydoc ContainerInterface::getProperty
    #
    #   Reimplemented from ContainerInterface.
    #
    #   getProperty will start at the top of the stack and try to get the property
    #   specified. If that container returns no value, the next container on the
    #   stack will be tried and so on until the bottom of the stack is reached.
    #   If a next stack is defined for this stack it will then try to get the
    #   value from that stack. If no next stack is defined, None will be returned.
    #
    #   Note that if the property value is a function, this method will return the
    #   result of evaluating that property with the current stack. If you need the
    #   actual function, use getRawProperty()
    def getProperty(self, key: str, property_name: str, context: Optional[PropertyEvaluationContext] = None):
        value = self.getRawProperty(key, property_name, context = context)
        if isinstance(value, SettingFunction):
            if context is not None:
                context.pushContainer(self)
            value = value(self, context)
            if context is not None:
                context.popContainer()

        return value

    ##  Retrieve a property of a setting by key and property name.
    #
    #   This method does the same as getProperty() except it does not perform any
    #   special handling of the result, instead the raw stored value is returned.
    #
    #   \param key The key to get the property value of.
    #   \param property_name The name of the property to get the value of.
    #   \param use_next True if the value should be retrieved from the next
    #   stack if not found in this stack. False if not.
    #   \param skip_until_container A container ID to skip to. If set, it will
    #   be as if all containers above the specified container are empty. If the
    #   container is not in the stack, it'll try to find it in the next stack.
    #
    #   \return The raw property value of the property, or None if not found. Note that
    #           the value might be a SettingFunction instance.
    #
    def getRawProperty(self, key, property_name, *, context: Optional[PropertyEvaluationContext] = None,
                       use_next = True, skip_until_container = None):
        containers = self._containers
        if context is not None:
            # if context is provided, check if there is any container that needs to be skipped.
            start_index = context.context.get("evaluate_from_container_index", 0)
            if start_index >= len(self._containers):
                return None
            containers = self._containers[start_index:]

        for container in containers:
            if skip_until_container and container.getId() != skip_until_container:
                continue #Skip.
            skip_until_container = None #When we find the container, stop skipping.

            value = container.getProperty(key, property_name, context)
            if value is not None:
                return value

        if self._next_stack and use_next:
            return self._next_stack.getRawProperty(key, property_name, context = context,
                                                   use_next = use_next, skip_until_container = skip_until_container)
        else:
            return None

    ##  \copydoc ContainerInterface::hasProperty
    #
    #   Reimplemented from ContainerInterface.
    #
    #   hasProperty will check if any of the containers in the stack has the
    #   specified property. If it does, it stops and returns True. If it gets to
    #   the end of the stack, it returns False.
    def hasProperty(self, key: str, property_name: str) -> bool:
        for container in self._containers:
            if container.hasProperty(key, property_name):
                return True

        if self._next_stack:
            return self._next_stack.hasProperty(key, property_name)
        return False

    # NOTE: we make propertyChanged and propertiesChanged as queued signals because otherwise, the emits in
    # _emitCollectedPropertyChanges() will be direct calls which modify the dict we are iterating over, and then
    # everything crashes.
    propertyChanged = Signal(Signal.Queued)
    propertiesChanged = Signal(Signal.Queued)

    ##  \copydoc ContainerInterface::serialize
    #
    #   Reimplemented from ContainerInterface
    #
    #   TODO: Expand documentation here, include the fact that this should _not_ include all containers
    def serialize(self, ignored_metadata_keys: Optional[set] = None):
        parser = configparser.ConfigParser(interpolation = None, empty_lines_in_values = False)

        parser["general"] = {}
        parser["general"]["version"] = str(self._metadata["version"])
        parser["general"]["name"] = str(self.getName())
        parser["general"]["id"] = str(self.getId())

        if ignored_metadata_keys is None:
            ignored_metadata_keys = set()
        ignored_metadata_keys |= {"id", "name", "version", "container_type"}
        parser["metadata"] = {}
        for key, value in self._metadata.items():
            # only serialize the data that's not in the ignore list
            if key not in ignored_metadata_keys:
                parser["metadata"][key] = str(value)

        parser.add_section("containers")
        for index in range(len(self._containers)):
            parser["containers"][str(index)] = str(self._containers[index].getId())

        stream = io.StringIO()
        parser.write(stream)
        return stream.getvalue()

    ##  Deserializes the given data and checks if the required fields are present.
    #
    #   The profile upgrading code depends on information such as "configuration_type" and "version", which come from
    #   the serialized data. Due to legacy problem, those data may not be available if it comes from an ancient Cura.
    @classmethod
    def _readAndValidateSerialized(cls, serialized: str) -> configparser.ConfigParser:
        parser = configparser.ConfigParser(interpolation=None, empty_lines_in_values=False)
        parser.read_string(serialized)

        if "general" not in parser or any(pn not in parser["general"] for pn in ("version", "name", "id")):
            raise InvalidContainerStackError("Missing required section 'general' or 'version' property")

        return parser

    @classmethod
    def getConfigurationTypeFromSerialized(cls, serialized: str) -> Optional[str]:
        configuration_type = None
        try:
            parser = cls._readAndValidateSerialized(serialized)
            configuration_type = parser["metadata"]["type"]
        except InvalidContainerStackError as icse:
            raise icse
        except Exception as e:
            Logger.log("e", "Could not get configuration type: %s", e)
        return configuration_type

    @classmethod
    def getVersionFromSerialized(cls, serialized: str) -> Optional[int]:
        configuration_type = cls.getConfigurationTypeFromSerialized(serialized)
        # get version
        version = None
        try:
            from UM.VersionUpgradeManager import VersionUpgradeManager
            version = VersionUpgradeManager.getInstance().getFileVersion(configuration_type, serialized)
        except Exception as e:
            Logger.log("d", "Could not get version from serialized: %s", e)
        return version

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    #
    #   TODO: Expand documentation here, include the fact that this should _not_ include all containers
    def deserialize(self, serialized, file_name = None) -> str:
        # update the serialized data first
        serialized = super().deserialize(serialized, file_name)
        parser = self._readAndValidateSerialized(serialized)

        if parser["general"].getint("version") != self.Version:
            raise IncorrectVersionError()

        # Clear all data before starting.
        for container in self._containers:
            container.propertyChanged.disconnect(self._collectPropertyChanges)

        self._containers = []
        self._metadata = {}

        if "metadata" in parser:
            self._metadata = dict(parser["metadata"])
        self._metadata["id"] = parser["general"]["id"]
        self._metadata["name"] = parser["general"].get("name", self.getId())
        self._metadata["version"] = self.Version #Guaranteed to be equal to what's in the container. See above.
        self._metadata["container_type"] = ContainerStack

        if "containers" in parser:
            for index, container_id in parser.items("containers"):
                containers = _containerRegistry.findContainers(id = container_id)
                if containers:
                    containers[0].propertyChanged.connect(self._collectPropertyChanges)
                    self._containers.append(containers[0])
                else:
                    self._containers.append(_containerRegistry.getEmptyInstanceContainer())
                    ConfigurationErrorMessage.getInstance().addFaultyContainers(container_id, self.getId())
                    Logger.log("e", "When trying to deserialize %s, we received an unknown container ID (%s)" % (self.getId(), container_id))
                    raise ContainerFormatError("When trying to deserialize %s, we received an unknown container ID (%s)" % (self.getId(), container_id))

        elif parser.has_option("general", "containers"):
            # Backward compatibility with 2.3.1: The containers used to be saved in a single comma-separated list.
            container_string = parser["general"].get("containers", "")
            Logger.log("d", "While deserializing, we got the following container string: %s", container_string)
            container_id_list = container_string.split(",")
            for container_id in container_id_list:
                if container_id != "":
                    containers = _containerRegistry.findContainers(id = container_id)
                    if containers:
                        containers[0].propertyChanged.connect(self._collectPropertyChanges)
                        self._containers.append(containers[0])
                    else:
                        self._containers.append(_containerRegistry.getEmptyInstanceContainer())
                        ConfigurationErrorMessage.getInstance().addFaultyContainers(container_id, self.getId())
                        Logger.log("e", "When trying to deserialize %s, we received an unknown container ID (%s)" % (self.getId(), container_id))
                        raise ContainerFormatError("When trying to deserialize %s, we received an unknown container ID (%s)" % (self.getId(), container_id))

        ## TODO; Deserialize the containers.

        return serialized

    ##  Gets the metadata of a container stack from a serialised format.
    #
    #   This parses the entire CFG document and only extracts the metadata from
    #   it.
    #
    #   \param serialized A CFG document, serialised as a string.
    #   \param container_id The ID of the container that we're getting the
    #   metadata of, as obtained from the file name.
    #   \return A dictionary of metadata that was in the CFG document as a
    #   singleton list. If anything went wrong, this returns an empty list
    #   instead.
    @classmethod
    def deserializeMetadata(cls, serialized: str, container_id: str) -> List[Dict[str, Any]]:
        serialized = cls._updateSerialized(serialized) #Update to most recent version.
        parser = configparser.ConfigParser(interpolation = None)
        parser.read_string(serialized)

        metadata = {
            "id": container_id,
            "container_type": ContainerStack
        }
        try:
            metadata["name"] = parser["general"]["name"]
            metadata["version"] = parser["general"]["version"]
        except KeyError as e: #One of the keys or the General section itself is missing.
            raise InvalidContainerStackError("Missing required fields: {error_msg}".format(error_msg = str(e)))

        if "metadata" in parser:
            metadata.update(parser["metadata"])

        return [metadata]

    ##  Get all keys known to this container stack.
    #
    #   In combination with getProperty(), you can obtain the current property
    #   values of all settings.
    #
    #   \return A set of all setting keys in this container stack.
    def getAllKeys(self) -> Set[str]:
        keys = set()    # type: Set[str]
        definition_containers = [container for container in self.getContainers() if container.__class__ == DefinitionContainer] #To get all keys, get all definitions from all definition containers.
        for definition_container in cast(List[DefinitionContainer], definition_containers):
            keys |= definition_container.getAllKeys()
        if self._next_stack:
            keys |= self._next_stack.getAllKeys()
        return keys

    ##  Get a list of all containers in this stack.
    #
    #   Note that it returns a shallow copy of the container list, as it's only allowed to change the order or entries
    #   in this list by the proper functions.
    #   \return \type{list} A list of all containers in this stack.
    def getContainers(self) -> List[ContainerInterface]:
        return self._containers[:]

    def getContainerIndex(self, container: ContainerInterface) -> int:
        return self._containers.index(container)

    ##  Get a container by index.
    #
    #   \param index \type{int} The index of the container to get.
    #
    #   \return The container at the specified index.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    def getContainer(self, index: int) -> ContainerInterface:
        if index < 0:
            raise IndexError
        return self._containers[index]

    ##  Get the container at the top of the stack.
    #
    #   This is a convenience method that will always return the top of the stack.
    #
    #   \return The container at the top of the stack, or None if no containers have been added.
    def getTop(self) -> Optional[ContainerInterface]:
        if self._containers:
            return self._containers[0]

        return None

    ##  Get the container at the bottom of the stack.
    #
    #   This is a convenience method that will always return the bottom of the stack.
    #
    #   \return The container at the bottom of the stack, or None if no containers have been added.
    def getBottom(self) -> Optional[ContainerInterface]:
        if self._containers:
            return self._containers[-1]

        return None

    ##  \copydoc ContainerInterface::getPath.
    #
    #   Reimplemented from ContainerInterface
    def getPath(self) -> str:
        return self._path

    ##  \copydoc ContainerInterface::setPath
    #
    #   Reimplemented from ContainerInterface
    def setPath(self, path: str):
        self._path = path

    ##  Get the SettingDefinition object for a specified key
    def getSettingDefinition(self, key: str):
        for container in self._containers:
            if not isinstance(container, DefinitionContainer):
                continue

            settings = container.findDefinitions(key = key)
            if settings:
                return settings[0]

        if self._next_stack:
            return self._next_stack.getSettingDefinition(key)
        else:
            return None

    ##  Find a container matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing key and value pairs
    #   that need to match the container. Note that the value of "*" can be used
    #   as a wild card. This will ensure that any container that has the
    #   specified key in the meta data is found.
    #   \param container_type \type{class} An optional type of container to
    #   filter on.
    #   \return The first container that matches the filter criteria or None if not found.
    @UM.FlameProfiler.profile
    def findContainer(self, criteria = None, container_type = None, **kwargs) -> Optional[ContainerInterface]:
        if not criteria and kwargs:
            criteria = kwargs
        elif criteria is None:
            criteria = {}

        for container in self._containers:
            meta_data = container.getMetaData()
            match = container.__class__ == container_type or container_type is None
            for key in criteria:
                if not match:
                    break
                try:
                    if meta_data[key] == criteria[key] or criteria[key] == "*":
                        continue
                    else:
                        match = False
                        break
                except KeyError:
                    match = False
                    break

            if match:
                return container

        return None

    ##  Add a container to the top of the stack.
    #
    #   \param container The container to add to the stack.
    def addContainer(self, container):
        self.insertContainer(0, container)

    ##  Insert a container into the stack.
    #
    #   \param index \type{int} The index of to insert the container at.
    #          A negative index counts from the bottom
    #   \param container The container to add to the stack.
    def insertContainer(self, index, container):
        if container is self:
            raise Exception("Unable to add stack to itself.")

        container.propertyChanged.connect(self._collectPropertyChanges)
        self._containers.insert(index, container)
        self.containersChanged.emit(container)

    ##  Replace a container in the stack.
    #
    #   \param index \type{int} The index of the container to replace.
    #   \param container The container to replace the existing entry with.
    #   \param postpone_emit  During stack manipulation you may want to emit later.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    #   \exception Exception when trying to replace container ContainerStack.
    def replaceContainer(self, index: int, container: ContainerInterface, postpone_emit=False):
        if index < 0:
            raise IndexError
        if container is self:
            raise Exception("Unable to replace container with ContainerStack (self) ")

        self._containers[index].propertyChanged.disconnect(self._collectPropertyChanges)
        container.propertyChanged.connect(self._collectPropertyChanges)
        self._containers[index] = container
        if postpone_emit:
            # send it using sendPostponedEmits
            self._postponed_emits.append((self.containersChanged, container))
        else:
            self.containersChanged.emit(container)

    ##  Remove a container from the stack.
    #
    #   \param index \type{int} The index of the container to remove.
    #
    #   \exception IndexError Raised when the specified index is out of bounds.
    def removeContainer(self, index: int = 0):
        if index < 0:
            raise IndexError
        try:
            container = self._containers[index]
            container.propertyChanged.disconnect(self._collectPropertyChanges)
            del self._containers[index]
            self.containersChanged.emit(container)
        except TypeError:
            raise IndexError("Can't delete container with index %s" % index)

    ##  Get the next stack
    #
    #   The next stack is the stack that is searched for a setting value if the
    #   bottom of the stack is reached when searching for a value.
    #
    #   \return \type{ContainerStack} The next stack or None if not set.
    def getNextStack(self) -> Optional["ContainerStack"]:
        return self._next_stack

    ##  Set the next stack
    #
    #   \param stack \type{ContainerStack} The next stack to set. Can be None.
    #   Raises Exception when trying to set itself as next stack (to prevent infinite loops)
    #   \sa getNextStack
    def setNextStack(self, stack: "ContainerStack", connect_signals: bool = True):
        if self is stack:
            raise Exception("Next stack can not be itself")
        if self._next_stack == stack:
            return

        if self._next_stack:
            self._next_stack.propertyChanged.disconnect(self._collectPropertyChanges)
            self.containersChanged.disconnect(self._next_stack.containersChanged)
        self._next_stack = stack
        if self._next_stack and connect_signals:
            self._next_stack.propertyChanged.connect(self._collectPropertyChanges)
            self.containersChanged.connect(self._next_stack.containersChanged)

    ##  Send postponed emits
    #   These emits are collected from the option postpone_emit.
    #   Note: the option can be implemented for all functions modifying the stack.
    def sendPostponedEmits(self):
        while self._postponed_emits:
            signal, signal_arg = self._postponed_emits.pop(0)
            signal.emit(signal_arg)

    ##  Check if the container stack has errors
    @UM.FlameProfiler.profile
    def hasErrors(self) -> bool:
        for key in self.getAllKeys():
            enabled = self.getProperty(key, "enabled")
            if not enabled:
                continue
            validation_state = self.getProperty(key, "validationState")
            if validation_state is None:
                # Setting is not validated. This can happen if there is only a setting definition.
                # We do need to validate it, because a setting defintions value can be set by a function, which could
                # be an invalid setting.
                definition = self.getSettingDefinition(key)
                validator_type = SettingDefinition.getValidatorForType(definition.type)
                if validator_type:
                    validator = validator_type(key)
                    validation_state = validator(self)
            if validation_state in (ValidatorState.Exception, ValidatorState.MaximumError, ValidatorState.MinimumError):
                return True
        return False

    ##  Get all the keys that are in an error state in this stack
    @UM.FlameProfiler.profile
    def getErrorKeys(self) -> List[str]:
        error_keys = []
        for key in self.getAllKeys():
            validation_state = self.getProperty(key, "validationState")
            if validation_state is None:
                # Setting is not validated. This can happen if there is only a setting definition.
                # We do need to validate it, because a setting defintions value can be set by a function, which could
                # be an invalid setting.
                definition = self.getSettingDefinition(key)
                validator_type = SettingDefinition.getValidatorForType(definition.type)
                if validator_type:
                    validator = validator_type(key)
                    validation_state = validator(self)
            if validation_state in (ValidatorState.Exception, ValidatorState.MaximumError, ValidatorState.MinimumError):
                error_keys.append(key)
        return error_keys

    # protected:

    # Gather up all signal emissions and delay their emit until the next time the event
    # loop can run. This prevents us from sending the same change signal multiple times.
    # In addition, it allows us to emit a single signal that reports all properties that
    # have changed.
    def _collectPropertyChanges(self, key: str, property_name: str):
        if key not in self._property_changes:
            self._property_changes[key] = set()

        self._property_changes[key].add(property_name)

        if not self._emit_property_changed_queued:
            from UM.Application import Application
            Application.getInstance().callLater(self._emitCollectedPropertyChanges)
            self._emit_property_changed_queued = True

    # Perform the emission of the change signals that were collected in a previous step.
    def _emitCollectedPropertyChanges(self):
        for key, property_names in self._property_changes.items():
            self.propertiesChanged.emit(key, property_names)

            for property_name in property_names:
                self.propertyChanged.emit(key, property_name)

        self._property_changes = {}
        self._emit_property_changed_queued = False

_containerRegistry = None   # type:  ContainerRegistryInterface

def setContainerRegistry(registry: ContainerRegistryInterface) -> None:
    global _containerRegistry
    _containerRegistry = registry
