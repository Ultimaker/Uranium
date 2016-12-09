# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser
import io
import copy

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType

import UM.Settings.ContainerRegistry

from . import ContainerInterface
from . import SettingInstance
from . import SettingRelation

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
#
@signalemitter
class InstanceContainer(ContainerInterface.ContainerInterface, PluginObject):
    Version = 2

    ##  Constructor
    #
    #   \param container_id A unique, machine readable/writable ID for this container.
    def __init__(self, container_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = str(container_id)
        self._name = container_id
        self._definition = None
        self._metadata = {}
        self._instances = {}
        self._read_only = False
        self._dirty = False
        self._path = ""
        self._postponed_emits = []

    def __hash__(self):
        # We need to re-implement the hash, because we defined the __eq__ operator.
        # According to some, returning the ID is technically not right, as objects with the same value should return
        # the same hash. The way we use it, it is acceptable for objects with the same value to return a different hash.
        return id(self)

    def __eq__(self, other):
        if type(self) != type(other):
            return False  # Type mismatch

        if self._id != other.getId():
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

    def __ne__(self, other):
        return not (self == other)

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self):
        return self._id

    id = property(getId)

    ##  \copydoc ContainerInterface::getPath.
    #
    #   Reimplemented from ContainerInterface
    def getPath(self):
        return self._path

    ##  \copydoc ContainerInterface::setPath
    #
    #   Reimplemented from ContainerInterface
    def setPath(self, path):
        self._path = path

    ##  \copydoc ContainerInterface::getName
    #
    #   Reimplemented from ContainerInterface
    def getName(self):
        return self._name

    name = property(getName)

    nameChanged = Signal()

    def setName(self, name):
        if name != self._name:
            self._name = name
            self._dirty = True
            self.nameChanged.emit()

    ##  \copydoc ContainerInterface::isReadOnly
    #
    #   Reimplemented from ContainerInterface
    def isReadOnly(self):
        return self._read_only

    def setReadOnly(self, read_only):
        self._read_only = read_only

    ##  \copydoc ContainerInterface::getMetaData
    #
    #   Reimplemented from ContainerInterface
    def getMetaData(self):
        return self._metadata

    metaData = property(getMetaData)
    metaDataChanged = Signal()

    def setMetaData(self, metadata):
        if metadata != self._metadata:
            self._metadata = metadata
            self._dirty = True
            self.metaDataChanged.emit(self)

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry, default = None):
        return self._metadata.get(entry, default)

    ##  Add a new entry to the metadata of this container.
    #
    #   \param key \type{str} The key of the new entry.
    #   \param value The value of the new entry.
    #
    #   \note This does nothing if the key already exists.
    def addMetaDataEntry(self, key, value):
        if key not in self._metadata:
            self._metadata[key] = value
            self._dirty = True
            self.metaDataChanged.emit(self)
        else:
            Logger.log("w", "Meta data with key %s was already added.", key)

    ##  Set a metadata entry to a certain value.
    #
    #   \param key The key of the metadata entry to set.
    #   \param value The new value of the metadata.
    #
    #   \note This does nothing if the key is not already added to the metadata.
    def setMetaDataEntry(self, key, value):
        if key in self._metadata:
            self._metadata[key] = value
            self._dirty = True
            self.metaDataChanged.emit(self)
        else:
            Logger.log("w", "Meta data with key %s was not found. Unable to change.", key)

    ##  Check if this container is dirty, that is, if it changed from deserialization.
    def isDirty(self):
        return self._dirty

    def setDirty(self, dirty):
        if self._read_only:
            Logger.log("w", "Tried to set dirty on read-only object.")
        else:
            self._dirty = dirty

    ##  \copydoc ContainerInterface::getProperty
    #
    #   Reimplemented from ContainerInterface
    def getProperty(self, key, property_name):
        if key in self._instances:
            try:
                return getattr(self._instances[key], property_name)
            except AttributeError:
                pass

        return None

    ##  \copydoc ContainerInterface::hasProperty
    #
    #   Reimplemented from ContainerInterface.
    def hasProperty(self, key, property_name):
        return key in self._instances and hasattr(self._instances[key], property_name)

    ##  Set the value of a property of a SettingInstance.
    #
    #   This will set the value of the specified property on the SettingInstance corresponding to key.
    #   If no instance has been created for the specified key, a new one will be created and inserted
    #   into this instance.
    #
    #   \param key \type{string} The key of the setting to set a property of.
    #   \param property_name \type{string} The name of the property to set.
    #   \param property_value The new value of the property.
    #   \param container The container to use for retrieving values when changing the property triggers property updates. Defaults to None, which means use the current container.
    #
    #   \note If no definition container is set for this container, new instances cannot be created and this method will do nothing.
    def setProperty(self, key, property_name, property_value, container = None):
        if self._read_only:
            Logger.log(
                "w",
                "Tried to setProperty [%s] with value [%s] with key [%s] on read-only object [%s]" % (
                    property_name, property_value, key, self.id))
            return
        if key not in self._instances:
            if not self._definition:
                Logger.log("w", "Tried to set value of setting %s that has no instance in container %s and the container has no definition", key, self._name)
                return

            setting_definition = self._definition.findDefinitions(key = key)
            if not setting_definition:
                Logger.log("w", "Tried to set value of setting %s that has no instance in container %s or its definition %s", key, self._name, self._definition.getName())
                return

            instance = SettingInstance.SettingInstance(setting_definition[0], self)
            instance.propertyChanged.connect(self.propertyChanged)
            self._instances[instance.definition.key] = instance

        self._instances[key].setProperty(property_name, property_value, container)

        self.setDirty(True)


    propertyChanged = Signal()

    ##  Remove all instances from this container.
    def clear(self):
        all_keys = self._instances.copy()
        for key in all_keys:
            self.removeInstance(key, postpone_emit=True)
        self.sendPostponedEmits()

    ##  Get all the keys of the instances of this container
    #   \returns list of keys
    def getAllKeys(self):
        return [key for key in self._instances]

    ##  Create a new InstanceContainer with the same contents as this container
    #
    #   \param new_id \type{str} The new ID of the container
    #   \param new_name \type{str} The new name of the container. Defaults to None to indicate the name should not change.
    #
    #   \return A new InstanceContainer with the same contents as this container.
    def duplicate(self, new_id, new_name = None):
        new_container = self.__class__(new_id)
        if new_name:
            new_container.setName(new_name)

        new_container.setMetaData(copy.deepcopy(self._metadata))
        new_container.setDefinition(self._definition)

        for instance_id in self._instances:
            instance = self._instances[instance_id]
            for property_name in instance.definition.getPropertyNames():
                if not hasattr(instance, property_name):
                    continue

                new_container.setProperty(instance.definition.key, property_name, getattr(instance, property_name))

        new_container._dirty = True
        new_container._read_only = False
        return new_container

    ##  \copydoc ContainerInterface::serialize
    #
    #   Reimplemented from ContainerInterface
    def serialize(self):
        parser = configparser.ConfigParser(interpolation = None)

        if not self._definition:
            Logger.log("w", "Tried to serialize an instance container without definition, this is not supported")
            return ""

        parser["general"] = {}
        parser["general"]["version"] = str(self.Version)
        parser["general"]["name"] = str(self._name)
        parser["general"]["definition"] = str(self._definition.getId())

        parser["metadata"] = {}
        for key, value in self._metadata.items():
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

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    def deserialize(self, serialized):
        parser = configparser.ConfigParser(interpolation = None)
        parser.read_string(serialized)

        has_general = "general" in parser
        has_version = "version" in parser["general"]
        has_definition = "definition" in parser["general"]

        if not has_general or not has_version or not has_definition:
            exception_string = "Missing the required"
            if not has_general:
                exception_string += " section 'general'"
            if not has_definition:
                exception_string += " property 'definition'"
            if not has_version:
                exception_string += " property 'version'"
            raise InvalidInstanceError(exception_string)

        if parser["general"].getint("version") != self.Version:
            raise IncorrectInstanceVersionError("Reported version {0} but expected version {1}".format(parser["general"].getint("version"), self.Version))

        # Reset old data
        self._metadata = {}
        self._instances = {}

        self._name = parser["general"].get("name", self._id)

        definition_id = parser["general"]["definition"]
        definitions = UM.Settings.ContainerRegistry.getInstance().findDefinitionContainers(id = definition_id)
        if not definitions:
            raise DefinitionNotFoundError("Could not find definition {0} required for instance {1}".format(definition_id, self._id))
        self._definition = definitions[0]

        if "metadata" in parser:
            self._metadata = dict(parser["metadata"])

        if "values" in parser:
            for key, value in parser["values"].items():
                self.setProperty(key, "value", value, self._definition)

        self._dirty = False

    ##  Find instances matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments with key-value pairs that should match properties of the instances.
    def findInstances(self, **kwargs):
        result = []
        for setting_key, instance in self._instances.items():
            for key, value in kwargs.items():
                if not hasattr(instance, key) or getattr(instance, key) != value:
                    break
            else:
                result.append(instance)

        return result

    ##  Get an instance by key
    #
    def getInstance(self, key):
        if key in self._instances:
            return self._instances[key]

        return None

    ##  Add a new instance to this container.
    def addInstance(self, instance):
        key = instance.definition.key
        if key in self._instances:
            return

        instance.propertyChanged.connect(self.propertyChanged)
        instance.propertyChanged.emit(key, "value")
        self._instances[key] = instance

    ##  Remove an instance from this container.
    #   /param postpone_emit postpone emit until calling sendPostponedEmits
    def removeInstance(self, key, postpone_emit=False):
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

    ##  Get the DefinitionContainer used for new instance creation.
    def getDefinition(self):
        return self._definition

    ##  Set the DefinitionContainer to use for new instance creation.
    #
    #   Since SettingInstance needs a SettingDefinition to work properly, we need some
    #   way of figuring out what SettingDefinition to use when creating a new SettingInstance.
    def setDefinition(self, definition):
        self._definition = definition

    def __lt__(self, other):
        own_weight = int(self.getMetaDataEntry("weight", 0))
        other_weight = int(other.getMetaDataEntry("weight", 0))

        if own_weight and other_weight:
            return own_weight < other_weight

        return self._name < other.name

    ##  Send postponed emits
    #   These emits are collected from the option postpone_emit.
    #   Note: the option can be implemented for all functions modifying the container.
    def sendPostponedEmits(self):
        while self._postponed_emits:
            signal, signal_arg = self._postponed_emits.pop(0)
            signal.emit(*signal_arg)
