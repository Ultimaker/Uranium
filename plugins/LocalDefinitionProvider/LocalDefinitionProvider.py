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

    def loadMetadata(self, container_id: str) -> Dict[str, Dict[str, Any]]:
        result = {}

        for filename in Resources.getAllResourcesOfType(Resources.DefinitionContainers):
            with open(filename) as f:
                metadata = DefinitionContainer.getMetadataFromSerialized(f.read())
            if metadata is None:
                continue

            #Always fill in the ID from the filename, rather than the ID in the metadata itself.
            metadata["id"] = os.path.basename(filename).split(".")[0] #Instead of using the default splitext function, we deal with multiple extensions differently: We always split on the first point.
            result[metadata["id"]] = metadata

        return result

    ##  Updates the cache of paths to definitions.
    #
    #   This way we can more easily load the definition files we want lazily.
    def _updatePathCache(self):
        self._id_to_path = {} #Clear cache first.

        for filename in Resources.getAllResourcesOfType(Resources.DefinitionContainers):
            definition_id = ".".join(os.path.basename(filename).split(".")[:-2]) #Remove the last two extensions.
            self._id_to_path[definition_id] = filename