# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, cast, Dict, Iterable, Optional

from UM.Logger import Logger
from UM.PluginObject import PluginObject #We're implementing this.
from UM.PluginRegistry import PluginRegistry #To get the priority metadata to sort by.
from UM.Settings.Interfaces import ContainerInterface

##  This class serves as a database for containers.
#
#   A plug-in can define a new source for containers by implementing the
#   ``getAllIds``, ``loadMetadata`` and ``loadContainer`` methods.
class ContainerProvider(PluginObject):
    ##  Initialises the provider, which creates a few empty fields.
    def __init__(self) -> None:
        super().__init__()

        #The container data, dictionaries indexed by ID.
        self._metadata = {} #type: Dict[str, Dict[str, Any]] #The metadata of all containers this provider can provide.
        self._containers = {} #type: Dict[str, ContainerInterface] #The complete containers that have been loaded so far. This is filled lazily upon requesting profiles.

    ##  Gets a container with a specified ID.
    #
    #   This should be implemented lazily. An implementation should first check
    #
    #   \param container_id The ID of a container to get.
    #   \return The specified container.
    def __getitem__(self, container_id: str) -> ContainerInterface:
        if container_id not in self._containers:
            try:
                self._containers[container_id] = self.loadContainer(container_id)
            except:
                Logger.logException("e", "Failed to load container %s", container_id)
                raise
        return self._containers[container_id]

    ##  Compares container providers by their priority so that they are easy to
    #   sort.
    #
    #   \param other The other container provider to compare with.
    #   \return A positive number if this provider has lower priority than the
    #   other, or a negative number if this provider has higher priority than
    #   the other.
    def __lt__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False
        other = cast(ContainerProvider, other)

        plugin_registry = PluginRegistry.getInstance()
        my_metadata = plugin_registry.getMetaData(self.getPluginId())
        other_metadata = plugin_registry.getMetaData(other.getPluginId())
        return my_metadata["container_provider"]["priority"] < other_metadata["container_provider"]["priority"]

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False
        other = cast(ContainerProvider, other)

        plugin_registry = PluginRegistry.getInstance()
        my_metadata = plugin_registry.getMetaData(self.getPluginId())
        other_metadata = plugin_registry.getMetaData(other.getPluginId())
        return my_metadata["container_provider"]["priority"] == other_metadata["container_provider"]["priority"]

    ##  Adds an item to the list of metadata.
    #
    #   This is intended to be called from the implementation of
    #   ``loadMetadata``.
    def addMetadata(self, metadata: Dict[str, Any]) -> None:
        if "id" not in metadata:
            raise ValueError("The specified metadata has no ID.")
        if metadata["id"] in self._metadata:
            raise KeyError("The specified metadata already exists.")
        self._metadata[metadata["id"]] = metadata

    ##  Gets the metadata of a specified container.
    #
    #   If the metadata of the container doesn't exist yet, it is loaded from
    #   the container source by the implementation of the provider.
    #
    #   Note that due to inheritance, this may also trigger the metadata of
    #   other containers to load.
    #
    #   \param container_id The container to get the metadata of.
    #   \return A dictionary of metadata for this container, or ``None`` if it
    #   failed to load.
    def getMetadata(self, container_id: str) -> Optional[Dict[str, Any]]:
        if container_id not in self._metadata:
            metadata = self.loadMetadata(container_id)
            if metadata is None:
                Logger.log("e", "Failed to load metadata of container %s", container_id)
                return None
        return self._metadata[container_id]

    # Gets the container file path with for the container with the given ID. Returns None if the container/file doesn't
    # exist.
    def getContainerFilePathById(self, container_id: str) -> Optional[str]:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement getAllIds.".format(class_name = self.__class__.__name__))

    ##  Gets a list of IDs of all containers this provider provides.
    #
    #   \return A list of all container IDs.
    def getAllIds(self) -> Iterable[str]:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement getAllIds.".format(class_name = self.__class__.__name__))

    ##  Returns whether a container is considered read-only by this provider.
    #
    #   Some providers don't allow modifying their containers at all. Some only
    #   allow some containers to be modified.
    #   \return Whether the specified container is read-only.
    def isReadOnly(self, container_id: str) -> bool:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement isReadOnly.".format(class_name = self.__class__.__name__))

    ##  Loads the container with the specified ID.
    #
    #   This is called lazily, so it should only request to load each container
    #   once and only when it's really needed. The container must be fully
    #   loaded after this is completed, so it may take some time.
    #
    #   \return The fully loaded container.
    def loadContainer(self, container_id: str) -> "ContainerInterface":
        raise NotImplementedError("The container provider {class_name} doesn't properly implement loadContainer.".format(class_name = self.__class__.__name__))

    ##  Loads the metadata of a specified container.
    #
    #   This will be called during start-up. It should be efficient.
    #
    #   \param container_id The ID of the container to load the metadata of.
    #   \return A dictionary of metadata dictionaries, indexed by their IDs.
    def loadMetadata(self, container_id: str) -> Dict[str, Any]:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement loadMetadata.".format(class_name = self.__class__.__name__))

    ##  Gets a dictionary of metadata of all containers, indexed by ID.
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        return self._metadata

    ##  Delete a container from this provider.
    #
    #   This deletes the container from the source. If it's read only, this
    #   should give an exception.
    #   \param container_id The ID of the container to remove.
    def removeContainer(self, container_id: str) -> None:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement removeContainer.".format(class_name = self.__class__.__name__))
