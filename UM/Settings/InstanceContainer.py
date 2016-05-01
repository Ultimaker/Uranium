# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.
import configparser

import io

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject
from UM.Logger import Logger

from . import ContainerInterface
from . import SettingInstance

class InvalidInstanceError(Exception):
    pass

class IncorrectInstanceVersionError(Exception):
    pass

##  A container for SettingInstance objects.
#
#
@signalemitter
class InstanceContainer(ContainerInterface.ContainerInterface, PluginObject):
    Version = 1

    ##  Constructor
    #
    #   \param container_id A unique, machine readable/writable ID for this container.
    def __init__(self, container_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = container_id
        self._name = container_id
        self._metadata = {}
        self._instances = {}

    ##  \copydoc ContainerInterface::getId
    #
    #   Reimplemented from ContainerInterface
    def getId(self):
        return self._id

    ##  \copydoc ContainerInterface::getName
    #
    #   Reimplemented from ContainerInterface
    def getName(self):
        return self._name

    ##  \copydoc ContainerInterface::getMetaData
    #
    #   Reimplemented from ContainerInterface
    def getMetaData(self):
        return self._metadata

    ##  \copydoc ContainerInterface::getMetaDataEntry
    #
    #   Reimplemented from ContainerInterface
    def getMetaDataEntry(self, entry, default = None):
        return self._metadata.get(entry, default)

    ##  \copydoc ContainerInterface::getValue
    #
    #   Reimplemented from ContainerInterface
    def getValue(self, key):
        if key in self._instances:
            return self._instances[key].value

        Logger.log("w", "Tried to get value of setting %s that has no instance in container %s", key, repr(self))
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
    def serialize(self, definition):
        parser = configparser.ConfigParser(interpolation = None, empty_lines_in_values = False)

        parser["general"] = {}
        parser["general"]["version"] = self.Version
        parser["general"]["name"] = self._name
        parser["general"]["definition"] = definition.getId()

        parser["metadata"] = {}
        for key, value in self._metadata.items():
            parser["metadata"][key] = value

        parser["values"] = {}
        for key, instance in self._instances:
            parser["values"][key] = instance.value

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

        if "metadata" in parser:
            self._metadata = parser["metadata"].copy()

        if "values" in parser:
            for key, value in parser["values"].items():
                if not key in self._instances:

                    self._instances[key] = SettingInstance.SettingInstance(definition, )

    ##  Find instances matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary with key-value pairs that should match properties of the instances.
    def findInstances(self, filter):
        return []

    def getInstance(self, key):
        if key in self._instances:
            return self._instances[key]

        return None

    def addInstance(self, instance):
        key = instance.definition.key
        if key in self._instances:
            return

        self._instances[key] = instance
