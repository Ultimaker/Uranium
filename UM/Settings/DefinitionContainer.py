# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import ContainerInterface

##  A container for SettingDefinition objects.
#
#
class DefinitionContainer(ContainerInterface.ContainerInterface):
    Version = 1

    ##  Constructor
    #
    #   \param container_id A unique, machine readable/writable ID for this container.
    def __init__(self, container_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = container_id
        self._name = container_id
        self._metadata = {}
        self._definitions = []

    ##  Reimplement __setattr__ so we can make sure the definition remains unchanged after creation.
    def __setattr__(self, name, value):
        raise NotImplementedError()

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

    ##  Find definitions matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing key-value pairs which should match properties of the definition.
    def findDefinitions(self, filter):
        return []
