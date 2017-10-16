# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os #To get the ID from a filename.
from typing import Any, Dict

from UM.Settings.ContainerProvider import ContainerProvider #The class we're implementing.
from UM.Settings.DefinitionContainer import DefinitionContainer #To parse JSON files and get their metadata.
from UM.Resources import Resources

class LocalDefinitionProvider(ContainerProvider):
    ##  Creates the local definition provider.
    #
    #   This creates a cache which translates definition IDs to their file
    #   names.
    def __init__(self):
        super().__init__()

        #Translates definition IDs to the path to where the file is located.
        self._id_to_path = {} # type: Dict[str, str]

        self._updatePathCache()

    def loadContainer(self, container_id: str) -> "ContainerInterface":
        pass

    ##  Load the metadata of a specified container.
    #
    #   \param container_id The ID of the container to load the metadata of.
    #   \return The metadata of the specified container, or ``None`` if the
    #   metadata failed to load.
    def loadMetadata(self, container_id: str) -> Dict[str, Any]:
        try:
            filename = self._id_to_path[container_id] #Raises KeyError if container ID does not exist in the (cache of the) files!
        except KeyError:
            #Update the cache. This shouldn't happen or be necessary because the list of definitions never changes during runtime, but let's update the cache just to be sure.
            self._updatePathCache()
            filename = self._id_to_path[container_id]
            #If we get another KeyError, pass that on up because that's a programming error for sure then.

        with open(filename) as f:
            metadata = DefinitionContainer.getMetadataFromSerialized(f.read())
            metadata["id"] = container_id #Always fill in the ID from the filename, rather than the ID in the metadata itself.
        return metadata

    ##  Updates the cache of paths to definitions.
    #
    #   This way we can more easily load the definition files we want lazily.
    def _updatePathCache(self):
        self._id_to_path = {} #Clear cache first.

        for filename in Resources.getAllResourcesOfType(Resources.DefinitionContainers):
            definition_id = ".".join(os.path.basename(filename).split(".")[:-2]) #Remove the last two extensions.
            self._id_to_path[definition_id] = filename