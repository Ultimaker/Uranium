# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os #For getting the IDs from a filename.
from typing import Any, Dict, Iterable, Optional
import urllib.parse #For getting the IDs from a filename.

from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType #To get the type of container we're loading.
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
        self._id_to_mime = {} # type: Dict[str, MimeType] #Translates container IDs to their MIME type.

        self._updatePathCache()

    ##  Gets the IDs of all local containers.
    #
    #   \return A sequence of all container IDs.
    def getAllIds(self) -> Iterable[str]:
        return self._id_to_path.keys()

    def loadContainer(self, container_id: str) -> "ContainerInterface":
        file_path = self._id_to_path[container_id] #Raises KeyError if container ID does not exist in the (cache of the) files!

        #The actual loading.
        container = self.__mime_to_class[self._id_to_mime[container_id].name](container_id)
        with open(file_path) as f:
            container.deserialize(f.read())
        container.setPath(file_path)

        #If the file is not in a subdirectory of the data storage path, it's read-only.
        storage_path = os.path.realpath(Resources.getDataStoragePath())
        read_only = os.path.commonpath([storage_path, os.path.realpath(file_path)]) != storage_path
        container.setReadOnly(read_only)

        return container

    ##  Load the metadata of a specified container.
    #
    #   \param container_id The ID of the container to load the metadata of.
    #   \return The metadata of the specified container, or ``None`` if the
    #   metadata failed to load.
    def loadMetadata(self, container_id: str) -> Optional[Dict[str, Any]]:
        filename = self._id_to_path[container_id] #Raises KeyError if container ID does not exist in the (cache of the) files!

        with open(filename) as f:
            metadata = self.__mime_to_class[self._id_to_mime[container_id].name].deserializeMetadata(f.read()) #pylint: disable=no-member
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
            container_id = mime.stripExtension(os.path.basename(filename))
            container_id = urllib.parse.unquote_plus(container_id)
            self._id_to_path[container_id] = filename
            self._id_to_mime[container_id] = mime

    ##  Maps MIME types to the class with which files of that type should be
    #   constructed.
    __mime_to_class = {
        "application/x-uranium-definitioncontainer": DefinitionContainer,
        "application/x-uranium-instancecontainer": InstanceContainer,
        "application/x-uranium-containerstack": ContainerStack
    }