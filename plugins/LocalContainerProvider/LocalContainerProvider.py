# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict, Iterable, Optional

from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase #To get the type of container we're loading.
from UM.Settings.ContainerProvider import ContainerProvider #The class we're implementing.
from UM.Settings.ContainerStack import ContainerStack #To parse CFG files and get their metadata, and to load ContainerStacks.
from UM.Settings.DefinitionContainer import DefinitionContainer #To parse JSON files and get their metadata, and to load DefinitionContainers.
from UM.Settings.InstanceContainer import InstanceContainer #To parse CFG files and get their metadata, and to load InstanceContainers.
from UM.Resources import Resources

##  Provides containers from the local installation.
class LocalContainerProvider(ContainerProvider):
    ##  Creates the local container provider.
    #
    #   This creates a cache which translates container IDs to their file names.
    def __init__(self):
        super().__init__()

        self._id_to_path = {} # type: Dict[str, str] #Translates container IDs to the path to where the file is located.
        self._id_to_class = {} # type: Dict[str, type] #Translates container IDs to their class.

        self._updatePathCache()

    ##  Gets the IDs of all local containers.
    #
    #   \return A sequence of all container IDs.
    def getAllIds(self) -> Iterable[str]:
        return self._id_to_path.keys()

    def loadContainer(self, container_id: str) -> "ContainerInterface":
        #Find the file name from the cache.
        filename = self._id_to_path[container_id] #Raises KeyError if container ID does not exist in the (cache of the) files!

        #The actual loading.
        container = self._id_to_class[container_id](container_id)
        with open(filename) as f:
            container.deserialize(f.read())
        return container

    ##  Load the metadata of a specified container.
    #
    #   \param container_id The ID of the container to load the metadata of.
    #   \return The metadata of the specified container, or ``None`` if the
    #   metadata failed to load.
    def loadMetadata(self, container_id: str) -> Optional[Dict[str, Any]]:
        try:
            filename = self._id_to_path[container_id] #Raises KeyError if container ID does not exist in the (cache of the) files!
        except KeyError:
            #Update the cache. This shouldn't happen or be necessary because the list of definitions never changes during runtime, but let's update the cache just to be sure.
            Logger.log("w", "Couldn't find definition file with ID {container_id}. Refreshing cache from resources and trying again...".format(container_id = container_id))
            self._updatePathCache()
            filename = self._id_to_path[container_id]
            #If we get another KeyError, pass that on up because that's a programming error for sure then.

        with open(filename) as f:
            metadata = DefinitionContainer.getMetadataFromSerialized(f.read())
        if metadata is None:
            return None
        metadata["id"] = container_id #Always fill in the ID from the filename, rather than the ID in the metadata itself.
        return metadata

    ##  Updates the cache of paths to containers.
    #
    #   This way we can more easily load the container files we want lazily.
    def _updatePathCache(self):
        self._id_to_path = {} #Clear cache first.

        all_resources = set() #Remove duplicates, since the Resources only finds resources by their directories.
        all_resources.union(Resources.getAllResourcesOfType(Resources.DefinitionContainers))
        all_resources.union(Resources.getAllResourcesOfType(Resources.InstanceContainers))
        all_resources.union(Resources.getAllResourcesOfType(Resources.ContainerStacks))
        for filename in all_resources:
            mime = MimeTypeDatabase.getMimeTypeForFile(filename)
            container_id = mime.stripExtension(filename)
            self._id_to_path[container_id] = filename
            self._id_to_class[container_id] = self.__mime_to_class[mime.name]

    ##  Maps MIME types to the class with which files of that type should be
    #   constructed.
    __mime_to_class = {
        "application/x-uranium-definitioncontainer": DefinitionContainer,
        "application/x-uranium-instancecontainer": InstanceContainer,
        "application/x-uranium-containerstack": ContainerStack
    }