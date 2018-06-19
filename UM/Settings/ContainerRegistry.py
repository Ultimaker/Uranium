# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import collections
import gc
import os
import pickle
import re
import time
from typing import Any, cast, Dict, List, Optional, TYPE_CHECKING

import UM.Util
from UM.Logging.Logger import Logger
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Resources import Resources
from UM.Settings.ContainerFormatError import ContainerFormatError
from UM.Settings.ContainerProvider import ContainerProvider
from . import ContainerQuery
from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.Interfaces import ContainerInterface, ContainerRegistryInterface, DefinitionContainerInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext

from .LocalContainerProvider import LocalContainerProvider

if TYPE_CHECKING:
    from UM.Application import Application


# The maximum amount of query results we should cache
MaxQueryCacheSize = 1000


##  Central class to manage all setting providers.
#
#   This class aggregates all data from all container providers. If only the
#   metadata is used, it requests the metadata lazily from the providers. If
#   more than that is needed, the entire container is requested from the
#   appropriate providers.
class ContainerRegistry(ContainerRegistryInterface):

    def __init__(self, application: "Application", *args, **kwargs) -> None:
        if ContainerRegistry.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        ContainerRegistry.__instance = self

        super().__init__()

        self._application = application  # type: Application

        self.empty_container = _EmptyInstanceContainer("empty")  # type: InstanceContainer
        self.empty_container.setMetaDataEntry("setting_version", self._application.SettingVersion)

        #Sorted list of container providers (keep it sorted by sorting each time you add one!).
        self._providers = []  # type: List[ContainerProvider]

        self.metadata = {}  # type: Dict[str, Dict[str, Any]]
        self._containers = {}  # type: Dict[str, ContainerInterface]
        self.source_provider = {}  # type: Dict[str, Optional[ContainerProvider]]

        # Ensure that the empty container is added to the ID cache.
        self.metadata["empty"] = self.empty_container.getMetaData()
        self._containers["empty"] = self.empty_container
        self.source_provider["empty"] = None
        self._resource_types = {"definition": Resources.DefinitionContainers}  # type: Dict[str, int]
        self._query_cache = collections.OrderedDict() #type: collections.OrderedDict # This should really be an ordered set but that does not exist...

        self._definition_cache_dir = ""  # type: str

    def initialize(self):
        self._definition_cache_dir = os.path.join(Resources.getCacheStoragePath(), "definitions")

        provider = LocalContainerProvider(self)
        self.addProvider(provider)

    @property
    def definition_cache_dir(self) -> str:
        return self._definition_cache_dir

    def addResourceType(self, resource_type: int, container_type: str) -> None:
        self._resource_types[container_type] = resource_type

    ##  Returns all resource types.
    def getResourceTypes(self) -> Dict[str, int]:
        return self._resource_types

    def getDefaultSaveProvider(self) -> "ContainerProvider":
        if len(self._providers) == 1:
            return self._providers[0]
        raise NotImplementedError("Not implemented default save provider for multiple providers")

    ##  Adds a container provider to search through containers in.
    def addProvider(self, provider: ContainerProvider) -> None:
        self._providers.append(provider)

    ##  Find all DefinitionContainer objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the
    #   DefinitionContainer. An asterisk in the values can be used to denote a
    #   wildcard.
    def findDefinitionContainers(self, **kwargs: Any) -> List[DefinitionContainerInterface]:
        return cast(List[DefinitionContainerInterface], self.findContainers(container_type = DefinitionContainer, **kwargs))

    ##  Get the metadata of all definition containers matching certain criteria.
    #
    #   \param kwargs A dictionary of keyword arguments containing keys and
    #   values that need to match the metadata. An asterisk in the values can be
    #   used to denote a wildcard.
    #   \return A list of metadata dictionaries matching the search criteria, or
    #   an empty list if nothing was found.
    def findDefinitionContainersMetadata(self, **kwargs: Any) -> List[Dict[str, Any]]:
        return cast(List[Dict[str, Any]], self.findContainersMetadata(container_type = DefinitionContainer, **kwargs))

    ##  Find all InstanceContainer objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the
    #   InstanceContainer. An asterisk in the values can be used to denote a
    #   wildcard.
    def findInstanceContainers(self, **kwargs: Any) -> List[InstanceContainer]:
        return cast(List[InstanceContainer], self.findContainers(container_type = InstanceContainer, **kwargs))

    ##  Find the metadata of all instance containers matching certain criteria.
    #
    #   \param kwargs A dictionary of keyword arguments containing keys and
    #   values that need to match the metadata. An asterisk in the values can be
    #   used to denote a wildcard.
    #   \return A list of metadata dictionaries matching the search criteria, or
    #   an empty list if nothing was found.
    def findInstanceContainersMetadata(self, **kwargs: Any) -> List[Dict[str, Any]]:
        return cast(List[Dict[str, Any]], self.findContainersMetadata(container_type = InstanceContainer, **kwargs))

    ##  Find all ContainerStack objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the ContainerStack.
    #   An asterisk in the values can be used to denote a wildcard.
    def findContainerStacks(self, **kwargs: Any) -> List[ContainerStack]:
        return cast(List[ContainerStack], self.findContainers(container_type = ContainerStack, **kwargs))

    ##  Find the metadata of all container stacks matching certain criteria.
    #
    #   \param kwargs A dictionary of keyword arguments containing keys and
    #   values that need to match the metadata. An asterisk in the values can be
    #   used to denote a wildcard.
    #   \return A list of metadata dictionaries matching the search criteria, or
    #   an empty list if nothing was found.
    def findContainerStacksMetadata(self, **kwargs: Any) -> List[Dict[str, Any]]:
        return cast(List[Dict[str, Any]], self.findContainersMetadata(container_type = ContainerStack, **kwargs))

    ##  Find all container objects matching certain criteria.
    #
    #   \param container_type If provided, return only objects that are
    #   instances or subclasses of container_type.
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the container. An
    #   asterisk can be used to denote a wildcard.
    #
    #   \return A list of containers matching the search criteria, or an empty
    #   list if nothing was found.
    def findContainers(self, *, ignore_case: bool = False, **kwargs: Any) -> List[ContainerInterface]:
        #Find the metadata of the containers and grab the actual containers from there.
        results_metadata = self.findContainersMetadata(ignore_case = ignore_case, **kwargs)
        result = []
        for metadata in results_metadata:
            if metadata["id"] in self._containers: #Already loaded, so just return that.
                result.append(self._containers[metadata["id"]])
            else: # Metadata is loaded, but not the actual data.
                provider = self.source_provider[metadata["id"]]
                if not provider:
                    Logger.log("w", "The metadata of container {container_id} was added during runtime, but no accompanying container was added.".format(container_id = metadata["id"]))
                    continue
                try:
                    new_container = provider.loadContainer(metadata["id"])
                except ContainerFormatError as e:
                    Logger.logException("e", "Error in the format of container {container_id}: {error_msg}".format(container_id = metadata["id"], error_msg = str(e)))
                    continue
                except Exception as e:
                    Logger.logException("e", "Error when loading container {container_id}: {error_msg}".format(container_id = metadata["id"], error_msg = str(e)))
                    continue
                self.addContainer(new_container)
                result.append(new_container)
        return result

    ##  Find the metadata of all container objects matching certain criteria.
    #
    #   \param container_type If provided, return only objects that are
    #   instances or subclasses of ``container_type``.
    #   \param kwargs A dictionary of keyword arguments containing keys and
    #   values that need to match the metadata. An asterisk can be used to
    #   denote a wildcard.
    #   \return A list of metadata dictionaries matching the search criteria, or
    #   an empty list if nothing was found.
    def findContainersMetadata(self, *, ignore_case: bool = False, **kwargs: Any) -> List[Dict[str, Any]]:
        #Create the query object.
        query = ContainerQuery.ContainerQuery(self, ignore_case = ignore_case, **kwargs)
        candidates = None

        if "id" in kwargs and kwargs["id"] is not None and "*" not in kwargs["id"] and not ignore_case:
            if kwargs["id"] not in self.metadata: #If we're looking for an unknown ID, try to lazy-load that one.
                if kwargs["id"] not in self.source_provider:
                    for candidate in self._providers:
                        if kwargs["id"] in candidate.getAllIds():
                            self.source_provider[kwargs["id"]] = candidate
                            break
                    else:
                        return []
                provider = self.source_provider[kwargs["id"]]
                if not provider:
                    Logger.log("w", "Metadata of container {container_id} is missing even though the container is added during run-time.")
                    return []
                metadata = provider.loadMetadata(kwargs["id"])
                self.metadata[metadata["id"]] = metadata
                self.source_provider[metadata["id"]] = provider

            #Since IDs are the primary key and unique we can now simply request the candidate and check if it matches all requirements.
            if kwargs["id"] not in self.metadata:
                return []
            candidates = [self.metadata[kwargs["id"]]]

        if query.isHashable() and query in self._query_cache:
            #If the exact same query is in the cache, we can re-use the query result.
            self._query_cache.move_to_end(query) #Query was used, so make sure to update its position so that it doesn't get pushed off as a rarely-used query.
            return self._query_cache[query].getResult()

        query.execute(candidates = candidates)

        # Only cache query result when it is hashable
        if query.isHashable():
            self._query_cache[query] = query

            if len(self._query_cache) > MaxQueryCacheSize:
                # Since we use an OrderedDict, we can use a simple FIFO scheme
                # to discard queries. As long as we properly update queries
                # that are being used, this results in the least used queries
                # to be discarded.
                self._query_cache.popitem(last = False)

        return query.getResult()

    def findDirtyContainers(self, *, ignore_case: bool = False, **kwargs: Any) -> List[ContainerInterface]:
        results_metadata = self.findContainersMetadata(ignore_case = ignore_case, **kwargs)

        result = []
        for metadata in results_metadata:
            if metadata["id"] not in self._containers: #Not yet loaded, so it can't be dirty.
                continue
            candidate = self._containers[metadata["id"]]
            if hasattr(candidate, "isDirty") and candidate.isDirty(): #type: ignore #Check for hasattr because only InstanceContainers and Stacks have this method.
                result.append(self._containers[metadata["id"]])
        return result

    def getEmptyInstanceContainer(self) -> InstanceContainer:
        return self.empty_container

    def isReadOnly(self, container_id: str) -> bool:
        provider = self.source_provider.get(container_id)
        if not provider:
            return False
        return provider.isReadOnly(container_id)

    def isLoaded(self, container_id: str) -> bool:
        return container_id in self._containers

    def loadAllMetadata(self) -> None:
        for provider in self._providers:
            for container_id in list(provider.getAllIds()):
                if container_id not in self.metadata:
                    metadata = provider.loadMetadata(container_id)
                    if metadata is None:
                        continue
                    self.metadata[container_id] = metadata
                    self.source_provider[container_id] = provider

    def load(self) -> None:
        gc.disable()
        resource_start_time = time.time()

        with self.lockCache():
            for provider in self._providers:
                for container_id in list(provider.getAllIds()):
                    if container_id not in self._containers:
                        try:
                            self._containers[container_id] = provider.loadContainer(container_id)
                        except:
                            Logger.logException("e", "Failed to load container %s", container_id)
                            raise
                        self.metadata[container_id] = self._containers[container_id].getMetaData()
                        self.source_provider[container_id] = provider

        gc.enable()
        Logger.log("d", "Loading data into container registry took %s seconds", time.time() - resource_start_time)

    def addContainer(self, container: ContainerInterface) -> None:
        container_id = container.getId()
        if container_id in self._containers:
            Logger.log("w", "Container with ID %s was already added.", container_id)
            return

        self.metadata[container_id] = container.getMetaData()
        self._containers[container_id] = container
        if container_id not in self.source_provider:
            self.source_provider[container_id] = None #Added during runtime.
        self._clearQueryCacheByContainer(container)
        Logger.log("d", "Container [%s] added.", container_id)

    def removeContainer(self, container_id: str) -> None:
        # Here we only need to check metadata because a container may not be loaded but its metadata must have been
        # loaded first.
        if container_id not in self.metadata:
            Logger.log("w", "Tried to delete container {container_id}, which doesn't exist or isn't loaded.".format(container_id = container_id))
            return  # Ignore.

        container = None
        if container_id in self._containers:
            container = self._containers[container_id]
            del self._containers[container_id]
        if container_id in self.metadata:
            del self.metadata[container_id]
        if container_id in self.source_provider:
            if self.source_provider[container_id] is not None:
                cast(ContainerProvider, self.source_provider[container_id]).removeContainer(container_id)
            del self.source_provider[container_id]

        if container is not None:
            self._clearQueryCacheByContainer(container)

        Logger.log("d", "Removed container %s", container_id)

    def renameContainer(self, container_id: str, new_name: str, new_id: Optional[str] = None) -> None:
        Logger.log("d", "Renaming container %s to %s", container_id, new_name)
        # Same as removeContainer(), metadata is always loaded but containers may not, so always check metadata.
        if container_id not in self.metadata:
            Logger.log("w", "Unable to rename container %s, because it does not exist", container_id)
            return

        container = self._containers.get(container_id)
        if container is None:
            container = self.findContainers(id = container_id)[0]
        container = cast(ContainerInterface, container)

        if new_name == container.getName():
            Logger.log("w", "Unable to rename container %s, because the name (%s) didn't change", container_id, new_name)
            return

        try:
            container.setName(new_name)  # type: ignore
        except TypeError: #Some containers don't allow setting the name.
            return
        if new_id is not None:
            source_provider = self.source_provider[container.getId()]
            del self._containers[container.getId()]
            del self.metadata[container.getId()]
            del self.source_provider[container.getId()]
            if source_provider is not None:
                source_provider.removeContainer(container.getId())
            container.getMetaData()["id"] = new_id
            self._containers[container.getId()] = container
            self.metadata[container.getId()] = container.getMetaData()
            self.source_provider[container.getId()] = None  # to be saved with saveSettings

        self._clearQueryCacheByContainer(container)

    def uniqueName(self, original: str) -> str:
        name = original.strip()

        num_check = re.compile(r"(.*?)\s*#\d+$").match(name)
        if num_check: #There is a number in the name.
            name = num_check.group(1) #Filter out the number.

        if not name: #Wait, that deleted everything!
            name = "Profile"
        elif not self.findContainersMetadata(id = original.strip(), ignore_case = True) and not self.findContainersMetadata(name = original.strip()):
            # Check if the stripped version of the name is unique (note that this can still have the number in it)
            return original.strip()

        unique_name = name
        i = 1
        while self.findContainersMetadata(id = unique_name, ignore_case = True) or self.findContainersMetadata(name = unique_name): #A container already has this name.
            i += 1 #Try next numbering.
            unique_name = "%s #%d" % (name, i) #Fill name like this: "Extruder #2".
        return unique_name

    @classmethod
    def addContainerTypeByName(cls, container_type: type, type_name: str, mime_type: str) -> None:
        cls.__container_types[type_name] = container_type
        cls.mime_type_map[mime_type] = container_type

    @classmethod
    def getMimeTypeForContainer(cls, container_type: type) -> Optional[MimeType]:
        try:
            mime_type_name = UM.Util.findKeyInDict(cls.mime_type_map, container_type)
            if mime_type_name:
                return MimeTypeDatabase.getMimeType(mime_type_name)
        except ValueError:
            Logger.log("w", "Unable to find mimetype for container %s", container_type)
        return None

    @classmethod
    def getContainerForMimeType(cls, mime_type):
        return cls.mime_type_map.get(mime_type.name, None)

    @classmethod
    def getContainerTypes(cls):
        return cls.__container_types.items()

    def saveContainer(self, container: "ContainerInterface", provider: Optional["ContainerProvider"] = None) -> None:
        if not hasattr(provider, "saveContainer"):
            provider = self.getDefaultSaveProvider()
        if not hasattr(container, "isDirty") or not container.isDirty():  # type: ignore
            return

        provider.saveContainer(container)  # type: ignore
        self.source_provider[container.getId()] = provider

    def saveDirtyContainers(self) -> None:
        # Lock file for "more" atomically loading and saving to/from config dir.
        with self.lockFile():
            # Save base files first
            for instance in self.findDirtyContainers(container_type = InstanceContainer):
                if instance.getId() == instance.getMetaData().get("base_file"):
                    self.saveContainer(instance)

            for instance in self.findDirtyContainers(container_type = InstanceContainer):
                self.saveContainer(instance)

            for stack in self.findContainerStacks():
                self.saveContainer(stack)

    def _loadCachedDefinition(self, definition_id: str, path: str) -> None:
        try:
            cache_path = Resources.getPath(Resources.Cache, "definitions", self._application.getVersion(), definition_id)

            cache_mtime = os.path.getmtime(cache_path)
            definition_mtime = os.path.getmtime(path)

            if definition_mtime > cache_mtime:
                # The definition is newer than the cached version, so ignore the cached version.
                Logger.log("d", "Definition file %s is newer than cache, ignoring cached version", path)
                return None

            definition = None
            with open(cache_path, "rb") as f:
                definition = pickle.load(f)

            for file_path in definition.getInheritedFiles():
                if os.path.getmtime(file_path) > cache_mtime:
                    return None

            return definition
        except FileNotFoundError:
            return None
        except Exception as e:
            # We could not load a cached version for some reason. Ignore it.
            Logger.logException("d", "Could not load cached definition for %s", path)
            return None

    def _saveCachedDefinition(self, definition: DefinitionContainer):
        cache_path = Resources.getStoragePath(Resources.Cache, "definitions", self._application.getVersion(), definition.id)

        # Ensure the cache path exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

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

    def _clearQueryCache(self, *args: Any, **kwargs: Any) -> None:
        self._query_cache.clear()

    def _clearQueryCacheByContainer(self, container: ContainerInterface) -> None:
        if isinstance(container, DefinitionContainer):
            container_type = DefinitionContainer  # type: type
        elif isinstance(container, InstanceContainer):
            container_type = InstanceContainer
        elif isinstance(container, ContainerStack):
            container_type = ContainerStack
        else:
            Logger.log("w", "While clearing query cache, we got an unrecognised base type (%s). Clearing entire cache instead", type(container))
            self._clearQueryCache()
            return

        for key in list(self._query_cache.keys()):
            if self._query_cache[key].getContainerType() == container_type or self._query_cache[key].getContainerType() is None:
                del self._query_cache[key]

    __container_types = {
        "definition": DefinitionContainer,
        "instance": InstanceContainer,
        "stack": ContainerStack,
    }

    mime_type_map = {
        "application/x-uranium-definitioncontainer": DefinitionContainer,
        "application/x-uranium-instancecontainer": InstanceContainer,
        "application/x-uranium-containerstack": ContainerStack,
        "application/x-uranium-extruderstack": ContainerStack
    }

    __instance = None  # type: ContainerRegistry

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "ContainerRegistry":
        return cls.__instance


class _EmptyInstanceContainer(InstanceContainer):
    def isDirty(self) -> bool:
        return False

    def getProperty(self, key: str, property_name: str, context: Optional[PropertyEvaluationContext] = None) -> Any:
        return None

    def setProperty(self, key: str, property_name: str, property_value: Any, container: ContainerInterface = None, set_from_cache: bool = False) -> None:
        Logger.log("e", "Setting property %s of container %s which should remain empty", key, self.getName())
        return

    def getConfigurationType(self) -> str:
        return ""  # FIXME: not sure if this is correct

    def serialize(self, ignored_metadata_keys: Optional[set] = None) -> str:
        return "[general]\n version = " + str(InstanceContainer.Version) + "\n name = empty\n definition = fdmprinter\n"
