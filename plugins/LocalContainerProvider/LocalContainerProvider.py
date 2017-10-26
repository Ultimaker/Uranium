# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os #For getting the IDs from a filename.
import pickle #For caching definitions.
import re #To detect back-up files in the ".../old/#/..." folders.
from typing import Any, Dict, Iterable, Optional
import urllib.parse #For getting the IDs from a filename.

from UM.Application import Application #To get the current version for finding the cache directory.
from UM.Logger import Logger
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
        container_class = self.__mime_to_class[self._id_to_mime[container_id].name]
        if issubclass(container_class, DefinitionContainer): #We may need to load these from the definition cache.
            container = self._loadCachedDefinition(container_id)
            if container: #Yes, it was cached!
                return container

        #Not cached, so load by deserialising.
        file_path = self._id_to_path[container_id] #Raises KeyError if container ID does not exist in the (cache of the) files.
        container = container_class(container_id) #Construct the container!
        with open(file_path) as f:
            container.deserialize(f.read())
        container.setPath(file_path)

        #If the file is not in a subdirectory of the data storage path, it's read-only.
        storage_path = os.path.realpath(Resources.getDataStoragePath())
        read_only = os.path.commonpath([storage_path, os.path.realpath(file_path)]) != storage_path
        container.setReadOnly(read_only)

        if issubclass(container_class, DefinitionContainer):
            self._saveCachedDefinition(container)

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

    ##  Load a pre-parsed definition container.
    #
    #   Definition containers can be quite expensive to load, so this loads a
    #   pickled version of the definition if one is available.
    #
    #   \param definition_id The ID of the definition to load from the cache.
    #   \return If a cached version was available, return it. If not, return
    #   ``None``.
    def _loadCachedDefinition(self, definition_id) -> Optional[DefinitionContainer]:
        definition_path = self._id_to_path[definition_id]
        cache_path = Resources.getPath(Resources.Cache, "definitions", Application.getInstance().getVersion(), definition_id)
        try:
            cache_mtime = os.path.getmtime(cache_path)
            definition_mtime = os.path.getmtime(definition_path)
        except FileNotFoundError: #Cache doesn't exist yet.
            return None

        if definition_mtime > cache_mtime:
            # The definition is newer than the cached version, so ignore the cached version.
            Logger.log("d", "Definition file {path} is newer than cache. Ignoring cached version.".format(path = definition_path))
            return None

        try:
            with open(cache_path, "rb") as f:
                definition = pickle.load(f)
        except Exception as e: #TODO: Switch to multi-catch once we've upgraded to Python 3.6. Catch: OSError, IOError, AttributeError, EOFError, ImportError, IndexError and UnpicklingError.
            Logger.log("w", "Failed to load definition {definition_id} from cached file: {error_msg}".format(definition_id = definition_id, error_msg = str(e)))
            return None

        try:
            for file_path in definition.getInheritedFiles():
                if os.path.getmtime(file_path) > cache_mtime:
                    return None
        except FileNotFoundError:
            return None #Cache for parent doesn't exist yet.

        return definition

    ##  Cache a definition container on disk.
    #
    #   Definition containers can be quite expensive to parse and load, so this
    #   pickles a container and saves the pre-parsed definition on disk.
    #
    #   \param definition The definition container to store.
    def _saveCachedDefinition(self, definition: DefinitionContainer):
        cache_path = Resources.getPath(Resources.Cache, "definitions", self.getApplication().getVersion, definition.id)

        #Ensure the cache path exists.
        os.makedirs(os.path.dirname(cache_path), exist_ok = True)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(definition, f, pickle.HIGHEST_PROTOCOL)
        except RecursionError:
            #Sometimes a recursion error in pickling occurs here.
            #The cause is unknown. It must be some circular reference in the definition instances or definition containers.
            #Instead of saving a partial cache and raising an exception, simply fail to save the cache.
            #See CURA-4024.
            Logger.log("w", "The definition cache for definition {definition_id} failed to pickle.".format(definition_id = definition.getId()))
            if os.path.exists(cache_path):
                os.remove(cache_path) #The pickling might be half-complete, which causes EOFError in Pickle when you load it later.

    ##  Updates the cache of paths to containers.
    #
    #   This way we can more easily load the container files we want lazily.
    def _updatePathCache(self):
        self._id_to_path = {} #Clear cache first.

        old_file_expression = re.compile(r"{sep}old{sep}\d+{sep}".format(sep = os.sep)) #To detect files that are back-ups. Matches on .../old/#/...

        all_resources = set() #Remove duplicates, since the Resources only finds resources by their directories.
        all_resources.union(Resources.getAllResourcesOfType(Resources.DefinitionContainers))
        all_resources.union(Resources.getAllResourcesOfType(Resources.InstanceContainers))
        all_resources.union(Resources.getAllResourcesOfType(Resources.ContainerStacks))
        for filename in all_resources:
            if re.search(old_file_expression, filename):
                continue #This is a back-up file from an old version.

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