# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject

from . import ContainerInterface

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
        self._instances = []

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
        return None

    ##  Emitted whenever the value of an instance in this container changes.
    valueChanged = Signal()

    ##  Set the value of an instance in this container.
    #
    #   \param key \type{string} The key of the instance to set the value of.
    #   \param value The new value of the instance.
    def setValue(self, key, value):
        pass

    ##  \copydoc ContainerInterface::serialize
    #
    #   Reimplemented from ContainerInterface
    def serialize(self):
        return ""

    ##  \copydoc ContainerInterface::deserialize
    #
    #   Reimplemented from ContainerInterface
    def deserialize(self, serialized):
        pass

    ##  Find instances matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary with key-value pairs that should match properties of the instances.
    def findInstances(self, filter):
        return []
