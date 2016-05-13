# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import configparser
import io

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject
from UM.Logger import Logger

import UM.Settings.ContainerRegistry

from . import ContainerInterface
from . import SettingInstance

class InvalidInstanceError(Exception):
    pass

class IncorrectInstanceVersionError(Exception):
    pass

class DefinitionNotFoundError(Exception):
    pass

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

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self):
        return self._id

    id = property(getId)

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
            self.nameChanged.emit()

    def getDefinition(self):
        return self._definition

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
            self.metaDataChanged.emit()

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry, default = None):
        return self._metadata.get(entry, default)

    def addMetaDataEntry(self, key, value):
        if key not in self._metadata:
            self._metadata[key] = value
        else:
            Logger.log("w", "Meta data with key %s was already added.", key)

    ##  \copydoc ContainerInterface::getValue
    #
    #   Reimplemented from ContainerInterface
    def getValue(self, key):
        if key in self._instances:
            return self._instances[key].value

        #Logger.log("w", "Tried to get value of setting %s that has no instance in container %s", key, repr(self))
        return None

    ##  Emitted whenever the value of an instance in this container changes.
    valueChanged = Signal()

    ##  Set the value of an instance in this container.
    #
    #   \param key \type{string} The key of the instance to set the value of.
    #   \param value The new value of the instance.
    def setValue(self, key, value):
        if key not in self._instances:
            Logger.log("w", "Tried to set value of setting %s that has no instance in container %s", key, repr(self))
            return

        self._instances[key].setProperty("value", value)

    ##  \copydoc ContainerInterface::serialize
    #
    #   Reimplemented from ContainerInterface
    def serialize(self):
        parser = configparser.ConfigParser(interpolation = None, empty_lines_in_values = False)

        if not self._definition:
            Logger.log("e", "Tried to serialize an instance container without definition, this is not supported")
            return ""

        parser["general"] = {}
        parser["general"]["version"] = str(self.Version)
        parser["general"]["name"] = str(self._name)
        parser["general"]["definition"] = str(self._definition.getId())

        parser["metadata"] = {}
        for key, value in self._metadata.items():
            parser["metadata"][key] = str(value)

        parser["values"] = {}
        for key, instance in self._instances.items():
            parser["values"][key] = str(instance.value)

        stream = io.StringIO()
        parser.write(stream)
        return stream.getvalue()

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    def deserialize(self, serialized):
        parser = configparser.ConfigParser(interpolation = None, empty_lines_in_values = False)
        parser.read_string(serialized)

        if not "general" in parser or not "version" in parser["general"] or not "definition" in parser["general"]:
            raise InvalidInstanceError("Missing required section 'general' or 'version' property")

        if parser["general"].getint("version") != self.Version:
            raise IncorrectInstanceVersionError("Reported version {0} but expected version {1}".format(parser["general"].getint("version"), self.Version))

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
                if not key in self._instances:
                    setting_definition = self._definition.findDefinitions(key = key)[0]
                    self._instances[key] = SettingInstance.SettingInstance(setting_definition, self)
                self._instances[key].setProperty("value", value)

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

    def getInstance(self, key):
        if key in self._instances:
            return self._instances[key]

        return None

    def addInstance(self, instance):
        key = instance.definition.key
        if key in self._instances:
            return

        self._instances[key] = instance

    def getDefinition(self):
        return self._definition

    def setDefinition(self, definition):
        self._definition = definition
