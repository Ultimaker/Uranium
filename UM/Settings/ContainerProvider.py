# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict

from UM.PluginObject import PluginObject #We're implementing this.
from UM.PluginRegistry import PluginRegistry #To get the priority metadata to sort by.

##  This class serves as a database for containers.
#
#   A plug-in can define a new source for containers by implementing the
#   ``loadMetadata`` and ``loadContainer`` methods.
class ContainerProvider(PluginObject):
    ##  Initialises the provider, which creates a few empty fields.
    def __init__(self):
        super().__init__()

        #The container data, dictionaries indexed by ID.
        self._metadata = {} #The metadata of all containers this provider can provide.
        self._containers = {} #The complete containers that have been loaded so far. This is filled lazily upon requesting profiles.

    ##  Gets a container with a specified ID.
    #
    #   This should be implemented lazily. An implementation should first check
    #
    #   \param container_id The ID of a container to get.
    #   \return The specified container.
    def __getitem__(self, container_id: str):
        if container_id not in self._containers:
            self._containers[container_id] = self.loadContainer(container_id)
        return self._containers[container_id]

    ##  Compares container providers by their priority so that they are easy to
    #   sort.
    #
    #   \param other The other container provider to compare with.
    #   \return A positive number if this provider has lower priority than the
    #   other, or a negative number if this provider has higher priority than
    #   the other.
    def __lt__(self, other: "ContainerProvider"):
        plugin_registry = PluginRegistry.getInstance()
        my_metadata = plugin_registry.getMetaData(self.getPluginId())
        other_metadata = plugin_registry.getMetaData(other.getPluginId())
        return my_metadata["priority"] < other_metadata["priority"]

    def __eq__(self, other: "ContainerProvider"):
        plugin_registry = PluginRegistry.getInstance()
        my_metadata = plugin_registry.getMetaData(self.getPluginId())
        other_metadata = plugin_registry.getMetaData(other.getPluginId())
        return my_metadata["priority"] == other_metadata["priority"]

    ##  Adds an item to the list of metadata.
    #
    #   This is intended to be called from the implementation of
    #   ``loadMetadata``.
    def addMetadata(self, metadata: Dict[str, Any]):
        if "id" not in metadata:
            raise ValueError("The specified metadata has no ID.")
        if metadata["id"] in self._metadata:
            raise KeyError("The specified metadata already exists.")
        self._metadata[metadata["id"]] = metadata

    ##  Loads the container with the specified ID.
    #
    #   This is called lazily, so it should only request to load each container
    #   once and only when it's really needed. The container must be fully
    #   loaded after this is completed, so it may take some time.
    #
    #   \return The fully loaded container.
    def loadContainer(self, container_id: str) -> "ContainerInterface":
        raise NotImplementedError("The container provider {class_name} doesn't properly implement loadContainer.".format(class_name = self.__class__.__name__))

    ##  Loads the metadata of all available containers.
    #
    #   This will be called during start-up. It should be efficient.
    #
    #   \return A dictionary of metadata dictionaries, indexed by their IDs.
    def loadMetadata(self) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement loadMetadata.".format(class_name = self.__class__.__name__))

    ##  Gets a dictionary of metadata of all containers, indexed by ID.
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        return self._metadata