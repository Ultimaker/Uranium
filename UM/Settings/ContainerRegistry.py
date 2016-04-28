# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.PluginRegistry import PluginRegistry
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase

##  Central class to manage all Setting containers.
#
#
class ContainerRegistry:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mime = MimeType(
            name = "application/x-uranium-definitioncontainer",
            comment = "Uranium Definition Container",
            suffixes = [ "def.json" ]
        )
        MimeTypeDatabase.addMimeType(mime)
        mime = MimeType(
            name = "application/x-uranium-instancecontainer",
            comment = "Uranium Instance Container",
            suffixes = [ "inst.cfg" ]
        )
        MimeTypeDatabase.addMimeType(mime)
        mime = MimeType(
            name = "application/x-uranium-containerstack",
            comment = "Uranium Container Stack",
            suffixes = [ "stack.cfg" ]
        )
        MimeTypeDatabase.addMimeType(mime)

        self._containers = []

        PluginRegistry.getInstance().addType("settings_container", self.addContainerType)

    ##  Find all DefinitionContainer objects matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing keys and values that need to match the metadata of the DefinitionContainer.
    def findDefinitionContainers(self, filter):
        return []

    ##  Find all InstanceContainer objects matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing keys and values that need to match the metadata of the InstanceContainer.
    def findInstanceContainers(self, filter):
        return []

    ##  Find all ContainerStack objects matching certain criteria.
    #
    #   \param filter \type{dict} A dictionary containing keys and values that need to match the metadata of the ContainerStack.
    def findContainerStacks(self, filter):
        return []

    ##  Add a container type that will be used to serialize/deserialize containers.
    #
    #   \param container An instance of the container type to add.
    def addContainerType(self, container):
        pass

    ##  Get the singleton instance for this class.
    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = ContainerRegistry()

        return cls.__instance

    __instance = None
