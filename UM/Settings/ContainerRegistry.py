# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import collections
import gc
import os
import pickle #For serializing/deserializing Python classes to binary files
import re #For finding containers with asterisks in the constraints and for detecting backup files.
import time
from typing import Any, cast, Dict, List, Optional, Set, Type, TYPE_CHECKING

import UM.Dictionary
import UM.FlameProfiler
from UM.LockFile import LockFile
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.PluginRegistry import PluginRegistry #To register the container type plug-ins and container provider plug-ins.
from UM.Resources import Resources
from UM.Settings.EmptyInstanceContainer import EmptyInstanceContainer
from UM.Settings.ContainerFormatError import ContainerFormatError
from UM.Settings.ContainerProvider import ContainerProvider
from UM.Settings.constant_instance_containers import empty_container
from . import ContainerQuery
from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.Interfaces import ContainerInterface, ContainerRegistryInterface, DefinitionContainerInterface
from UM.Signal import Signal, signalemitter

if TYPE_CHECKING:
    from UM.PluginObject import PluginObject
    from UM.Qt.QtApplication import QtApplication


@signalemitter
class ContainerRegistry(ContainerRegistryInterface):
    """Central class to manage all setting providers.

    This class aggregates all data from all container providers. If only the
    metadata is used, it requests the metadata lazily from the providers. If
    more than that is needed, the entire container is requested from the
    appropriate providers.
    """

    def __init__(self, application: "QtApplication") -> None:
        if ContainerRegistry.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        ContainerRegistry.__instance = self

        super().__init__()

        self._application = application  # type: QtApplication

        self._emptyInstanceContainer = empty_container  # type: InstanceContainer

        # Sorted list of container providers (keep it sorted by sorting each time you add one!).
        self._providers = []  # type: List[ContainerProvider]
        PluginRegistry.addType("container_provider", self.addProvider)

        self.metadata = {}  # type: Dict[str, Dict[str, Any]]
        self._containers = {}  # type: Dict[str, ContainerInterface]
        self._wrong_container_ids = set() # type: Set[str]  # Set of already known wrong containers that must be skipped
        self.source_provider = {}  # type: Dict[str, Optional[ContainerProvider]]  # Where each container comes from.
        # Ensure that the empty container is added to the ID cache.
        self.metadata["empty"] = self._emptyInstanceContainer.getMetaData()
        self._containers["empty"] = self._emptyInstanceContainer
        self.source_provider["empty"] = None
        self._resource_types = {"definition": Resources.DefinitionContainers}  # type: Dict[str, int]

        #Since queries are based on metadata, we need to make sure to clear the cache when a container's metadata changes.
        self.containerMetaDataChanged.connect(self._clearQueryCache)

        self._explicit_read_only_container_ids = set()  # type: Set[str]

    containerAdded = Signal()
    containerRemoved = Signal()
    containerMetaDataChanged = Signal()
    containerLoadComplete = Signal()
    allMetadataLoaded = Signal()

    def addResourceType(self, resource_type: int, container_type: str) -> None:
        self._resource_types[container_type] = resource_type

    def getResourceTypes(self) -> Dict[str, int]:
        """Returns all resource types."""

        return self._resource_types

    def getDefaultSaveProvider(self) -> "ContainerProvider":
        if len(self._providers) == 1:
            return self._providers[0]
        raise NotImplementedError("Not implemented default save provider for multiple providers")

    def addWrongContainerId(self, wrong_container_id: str) -> None:
        """This method adds the current id to the list of wrong containers that are skipped when looking for a container"""

        self._wrong_container_ids.add(wrong_container_id)

    def addProvider(self, provider: ContainerProvider) -> None:
        """Adds a container provider to search through containers in."""

        self._providers.append(provider)
        # Re-sort every time. It's quadratic, but there shouldn't be that many providers anyway...
        self._providers.sort(key = lambda provider: PluginRegistry.getInstance().getMetaData(provider.getPluginId())["container_provider"].get("priority", 0))

    def findDefinitionContainers(self, **kwargs: Any) -> List[DefinitionContainerInterface]:
        """Find all DefinitionContainer objects matching certain criteria.

        :param dict kwargs: A dictionary of keyword arguments containing
        keys and values that need to match the metadata of the
        DefinitionContainer. An asterisk in the values can be used to denote a
        wildcard.
        """

        return cast(List[DefinitionContainerInterface], self.findContainers(container_type = DefinitionContainer, **kwargs))

    def findDefinitionContainersMetadata(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Get the metadata of all definition containers matching certain criteria.

        :param kwargs: A dictionary of keyword arguments containing keys and
        values that need to match the metadata. An asterisk in the values can be
        used to denote a wildcard.
        :return: A list of metadata dictionaries matching the search criteria, or
        an empty list if nothing was found.
        """

        return self.findContainersMetadata(container_type = DefinitionContainer, **kwargs)

    def findInstanceContainers(self, **kwargs: Any) -> List[InstanceContainer]:
        """Find all InstanceContainer objects matching certain criteria.

        :param kwargs: A dictionary of keyword arguments containing
        keys and values that need to match the metadata of the
        InstanceContainer. An asterisk in the values can be used to denote a
        wildcard.
        """

        return cast(List[InstanceContainer], self.findContainers(container_type = InstanceContainer, **kwargs))

    def findInstanceContainersMetadata(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Find the metadata of all instance containers matching certain criteria.

        :param kwargs: A dictionary of keyword arguments containing keys and
        values that need to match the metadata. An asterisk in the values can be
        used to denote a wildcard.
        :return: A list of metadata dictionaries matching the search criteria, or
        an empty list if nothing was found.
        """

        return self.findContainersMetadata(container_type = InstanceContainer, **kwargs)

    def findContainerStacks(self, **kwargs: Any) -> List[ContainerStack]:
        """Find all ContainerStack objects matching certain criteria.

        :param kwargs: A dictionary of keyword arguments containing
        keys and values that need to match the metadata of the ContainerStack.
        An asterisk in the values can be used to denote a wildcard.
        """

        return cast(List[ContainerStack], self.findContainers(container_type = ContainerStack, **kwargs))

    def findContainerStacksMetadata(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Find the metadata of all container stacks matching certain criteria.

        :param kwargs: A dictionary of keyword arguments containing keys and
        values that need to match the metadata. An asterisk in the values can be
        used to denote a wildcard.
        :return: A list of metadata dictionaries matching the search criteria, or
        an empty list if nothing was found.
        """

        return self.findContainersMetadata(container_type = ContainerStack, **kwargs)

    @UM.FlameProfiler.profile
    def findContainers(self, *, ignore_case: bool = False, **kwargs: Any) -> List[ContainerInterface]:
        """Find all container objects matching certain criteria.

        :param container_type: If provided, return only objects that are
        instances or subclasses of container_type.
        :param kwargs: A dictionary of keyword arguments containing
        keys and values that need to match the metadata of the container. An
        asterisk can be used to denote a wildcard.

        :return: A list of containers matching the search criteria, or an empty
        list if nothing was found.
        """

        # Find the metadata of the containers and grab the actual containers from there.
        results_metadata = self.findContainersMetadata(ignore_case = ignore_case, **kwargs)
        result = []
        for metadata in results_metadata:
            if metadata["id"] in self._containers:  # Already loaded, so just return that.
                result.append(self._containers[metadata["id"]])
            else:  # Metadata is loaded, but not the actual data.
                if metadata["id"] in self._wrong_container_ids:
                    Logger.logException("e", "Error when loading container {container_id}: This is a weird container, probably some file is missing".format(container_id = metadata["id"]))
                    continue
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
                self.containerLoadComplete.emit(new_container.getId())
                result.append(new_container)
        return result

    def findContainersMetadata(self, *, ignore_case: bool = False, **kwargs: Any) -> List[Dict[str, Any]]:
        """Find the metadata of all container objects matching certain criteria.

        :param container_type: If provided, return only objects that are
        instances or subclasses of ``container_type``.
        :param kwargs: A dictionary of keyword arguments containing keys and
        values that need to match the metadata. An asterisk can be used to
        denote a wildcard.
        :return: A list of metadata dictionaries matching the search criteria, or
        an empty list if nothing was found.
        """

        candidates = None
        if "id" in kwargs and kwargs["id"] is not None and "*" not in kwargs["id"] and not ignore_case:
            if kwargs["id"] not in self.metadata:  # If we're looking for an unknown ID, try to lazy-load that one.
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
                if metadata is None or metadata.get("id", "") in self._wrong_container_ids or "id" not in metadata:
                    return []
                self.metadata[metadata["id"]] = metadata
                self.source_provider[metadata["id"]] = provider

            # Since IDs are the primary key and unique we can now simply request the candidate and check if it matches all requirements.
            if kwargs["id"] not in self.metadata:
                return []  # Still no result, so return an empty list.
            if len(kwargs) == 1:
                return [self.metadata[kwargs["id"]]]
            candidates = [self.metadata[kwargs["id"]]]
            del kwargs["id"]  # No need to check for the ID again.

        query = ContainerQuery.ContainerQuery(self, ignore_case = ignore_case, **kwargs)
        query.execute(candidates = candidates)

        return cast(List[Dict[str, Any]], query.getResult())  # As the execute of the query is done, result won't be none.

    def findDirtyContainers(self, *, ignore_case: bool = False, **kwargs: Any) -> List[ContainerInterface]:
        """Specialized find function to find only the modified container objects
        that also match certain criteria.

        This is faster than the normal find methods since it won't ever load all
        containers, but only the modified ones. Since containers must be fully
        loaded before they are modified, you are guaranteed that any operations
        on the resulting containers will not trigger additional containers to
        load lazily.

        :param kwargs: A dictionary of keyword arguments containing
        keys and values that need to match the metadata of the container. An
        asterisk can be used to denote a wildcard.
        :param ignore_case: Whether casing should be ignored when matching string
        values of metadata.
        :return: A list of containers matching the search criteria, or an empty
        list if nothing was found.
        """

        # Find the metadata of the containers and grab the actual containers from there.
        #
        # We could apply the "is in self._containers" filter and the "isDirty" filter
        # to this metadata find function as well to filter earlier, but since the
        # filters in findContainersMetadata are applied in arbitrary order anyway
        # this will have very little effect except to prevent a list copy.
        results_metadata = self.findContainersMetadata(ignore_case = ignore_case, **kwargs)

        result = []
        for metadata in results_metadata:
            if metadata["id"] not in self._containers:  # Not yet loaded, so it can't be dirty.
                continue
            candidate = self._containers[metadata["id"]]
            if candidate.isDirty():
                result.append(self._containers[metadata["id"]])
        return result

    def getEmptyInstanceContainer(self) -> InstanceContainer:
        """This is a small convenience to make it easier to support complex structures in ContainerStacks."""

        return self._emptyInstanceContainer

    def setExplicitReadOnly(self, container_id: str) -> None:
        self._explicit_read_only_container_ids.add(container_id)

    def isExplicitReadOnly(self, container_id: str) -> bool:
        return container_id in self._explicit_read_only_container_ids

    def isReadOnly(self, container_id: str) -> bool:
        """Returns whether a profile is read-only or not.

        Whether it is read-only depends on the source where the container is
        obtained from.
        :return: True if the container is read-only, or False if it can be
        modified.
        """

        if self.isExplicitReadOnly(container_id):
            return True
        provider = self.source_provider.get(container_id)
        if not provider:
            return False  # If no provider had the container, that means that the container was only in memory. Then it's always modifiable.
        return provider.isReadOnly(container_id)

    # Gets the container file path with for the container with the given ID. Returns None if the container/file doesn't
    # exist.
    def getContainerFilePathById(self, container_id: str) -> Optional[str]:
        provider = self.source_provider.get(container_id)
        if not provider:
            return None
        return provider.getContainerFilePathById(container_id)

    def isLoaded(self, container_id: str) -> bool:
        """Returns whether a container is completely loaded or not.

        If only its metadata is known, it is not yet completely loaded.
        :return: True if all data about this container is known, False if only
        metadata is known or the container is completely unknown.
        """

        return container_id in self._containers

    def loadAllMetadata(self) -> None:
        """Load the metadata of all available definition containers, instance
        containers and container stacks.
        """

        self._clearQueryCache()
        gc.disable()
        resource_start_time = time.time()
        for provider in self._providers:  # Automatically sorted by the priority queue.
            for container_id in list(provider.getAllIds()):  # Make copy of all IDs since it might change during iteration.
                if container_id not in self.metadata:
                    self._application.processEvents()  # Update the user interface because loading takes a while. Specifically the loading screen.
                    metadata = provider.loadMetadata(container_id)
                    if not self._isMetadataValid(metadata):
                        Logger.log("w", "Invalid metadata for container {container_id}: {metadata}".format(container_id = container_id, metadata = metadata))
                        if container_id in self.metadata:
                            del self.metadata[container_id]
                        continue
                    self.metadata[container_id] = metadata
                    self.source_provider[container_id] = provider
        Logger.log("d", "Loading metadata into container registry took %s seconds", time.time() - resource_start_time)
        gc.enable()
        ContainerRegistry.allMetadataLoaded.emit()

    @UM.FlameProfiler.profile
    def load(self) -> None:
        """Load all available definition containers, instance containers and
        container stacks.

        :note This method does not clear the internal list of containers. This means that any containers
        that were already added when the first call to this method happened will not be re-added.
        """

        # Disable garbage collection to speed up the loading (at the cost of memory usage).
        gc.disable()
        resource_start_time = time.time()

        with self.lockCache():  # Because we might be writing cache files.
            for provider in self._providers:
                for container_id in list(provider.getAllIds()):  # Make copy of all IDs since it might change during iteration.
                    if container_id not in self._containers:
                        # Update UI while loading.
                        self._application.processEvents()  # Update the user interface because loading takes a while. Specifically the loading screen.
                        try:
                            self._containers[container_id] = provider.loadContainer(container_id)
                        except:
                            Logger.logException("e", "Failed to load container %s", container_id)
                            raise
                        self.metadata[container_id] = self._containers[container_id].getMetaData()
                        self.source_provider[container_id] = provider
                        self.containerLoadComplete.emit(container_id)

        gc.enable()
        Logger.log("d", "Loading data into container registry took %s seconds", time.time() - resource_start_time)

    @UM.FlameProfiler.profile
    def addContainer(self, container: ContainerInterface) -> bool:
        container_id = container.getId()
        if container_id in self._containers:
            return True  # Container was already there, consider that a success

        if hasattr(container, "metaDataChanged"):
            container.metaDataChanged.connect(self._onContainerMetaDataChanged)

        self.metadata[container_id] = container.getMetaData()
        self._containers[container_id] = container
        if container_id not in self.source_provider:
            self.source_provider[container_id] = None  # Added during runtime.
        self._clearQueryCacheByContainer(container)

        # containerAdded is a custom signal and can trigger direct calls to its subscribers. This should be avoided
        # because with the direct calls, the subscribers need to know everything about what it tries to do to avoid
        # triggering this signal again, which eventually can end up exceeding the max recursion limit.
        # We avoid the direct calls here to make sure that the subscribers do not need to take into account any max
        # recursion problem.
        self._application.callLater(self.containerAdded.emit, container)
        return True

    @UM.FlameProfiler.profile
    def removeContainer(self, container_id: str) -> None:
        # Here we only need to check metadata because a container may not be loaded but its metadata must have been
        # loaded first.
        if container_id not in self.metadata:
            Logger.log("w", "Tried to delete container {container_id}, which doesn't exist or isn't loaded.".format(container_id = container_id))
            return  # Ignore.

        # CURA-6237
        # Do not try to operate on invalid containers because removeContainer() needs to load it if it's not loaded yet
        # (see below), but an invalid container cannot be loaded.
        if container_id in self._wrong_container_ids:
            Logger.log("w", "Container [%s] is faulty, it won't be able to be loaded, so no need to remove, skip.")
            # delete the metadata if present
            if container_id in self.metadata:
                del self.metadata[container_id]
            return

        container = None
        if container_id in self._containers:
            container = self._containers[container_id]
            if hasattr(container, "metaDataChanged"):
                container.metaDataChanged.disconnect(self._onContainerMetaDataChanged)
            del self._containers[container_id]
        if container_id in self.metadata:
            if container is None:
                # We're in a bit of a weird state now. We want to notify the rest of the code that the container
                # has been deleted, but due to lazy loading, it hasn't been loaded yet. The issues is that in order
                # to notify the rest of the code, we need to actually *have* the container. So an empty instance 
                # container is created, which is emitted with the containerRemoved signal and contains the metadata
                container = EmptyInstanceContainer(container_id)
                container.metaData = self.metadata[container_id]
            del self.metadata[container_id]
        if container_id in self.source_provider:
            if self.source_provider[container_id] is not None:
                cast(ContainerProvider, self.source_provider[container_id]).removeContainer(container_id)
            del self.source_provider[container_id]

        if container is not None:
            self._clearQueryCacheByContainer(container)
            self.containerRemoved.emit(container)

        Logger.log("d", "Removed container %s", container_id)

    @UM.FlameProfiler.profile
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

        self.containerRemoved.emit(container)

        try:
            container.setName(new_name) #type: ignore
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
        self.containerAdded.emit(container)

    @UM.FlameProfiler.profile
    def uniqueName(self, original: str) -> str:
        """Creates a new unique name for a container that doesn't exist yet.

        It tries if the original name you provide exists, and if it doesn't
        it'll add a "        1" or "        2" after the name to make it unique.

        :param original: The original name that may not be unique.
        :return: A unique name that looks a lot like the original but may have
        a number behind it to make it unique.
        """

        original = original.replace("*", "")  # Filter out wildcards, since this confuses the ContainerQuery.
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
    def addContainerType(cls, container: "PluginObject") -> None:
        """Add a container type that will be used to serialize/deserialize containers.

        :param container: An instance of the container type to add.
        """

        plugin_id = container.getPluginId()
        metadata = PluginRegistry.getInstance().getMetaData(plugin_id)
        if "settings_container" not in metadata or "mimetype" not in metadata["settings_container"]:
            raise Exception("Plugin {plugin} has incorrect metadata: Expected a 'settings_container' block with a 'mimetype' entry".format(plugin = plugin_id))
        cls.addContainerTypeByName(container.__class__, plugin_id, metadata["settings_container"]["mimetype"])

    @classmethod
    def addContainerTypeByName(cls, container_type: type, type_name: str, mime_type: str) -> None:
        """Used to associate mime types with object to be created
        :param container_type:  ContainerStack or derivative
        :param type_name:
        :param mime_type:
        """

        cls.__container_types[type_name] = container_type
        cls.mime_type_map[mime_type] = container_type

    @classmethod
    def getMimeTypeForContainer(cls, container_type: type) -> Optional[MimeType]:
        """Retrieve the mime type corresponding to a certain container type

        :param container_type: The type of container to get the mime type for.

        :return: A MimeType object that matches the mime type of the container or None if not found.
        """

        try:
            mime_type_name = UM.Dictionary.findKey(cls.mime_type_map, container_type)
            if mime_type_name:
                return MimeTypeDatabase.getMimeType(mime_type_name)
        except ValueError:
            Logger.log("w", "Unable to find mimetype for container %s", container_type)
        return None

    @classmethod
    def getContainerForMimeType(cls, mime_type):
        """Get the container type corresponding to a certain mime type.

        :param mime_type: The mime type to get the container type for.

        :return: A class object of a container type that corresponds to the specified mime type or None if not found.
        """

        return cls.mime_type_map.get(mime_type.name, None)

    @classmethod
    def getContainerTypes(cls):
        """Get all the registered container types

        :return: A dictionary view object that provides access to the container types.
        The key is the plugin ID, the value the container type.
        """

        return cls.__container_types.items()

    def saveContainer(self, container: "ContainerInterface", provider: Optional["ContainerProvider"] = None) -> None:
        """Save single dirty container"""

        if not hasattr(provider, "saveContainer"):
            provider = self.getDefaultSaveProvider()
        if not container.isDirty():
            return

        provider.saveContainer(container) #type: ignore
        container.setDirty(False)
        self.source_provider[container.getId()] = provider

    def saveDirtyContainers(self) -> None:
        """Save all the dirty containers by calling the appropriate container providers"""

        # Lock file for "more" atomically loading and saving to/from config dir.
        with self.lockFile():
            for instance in self.findDirtyContainers(container_type = InstanceContainer):
                self.saveContainer(instance)

            for stack in self.findContainerStacks():
                self.saveContainer(stack)

    # Clear the internal query cache
    def _clearQueryCache(self, *args: Any, **kwargs: Any) -> None:
        ContainerQuery.ContainerQuery.cache.clear()

    def _clearQueryCacheByContainer(self, container: ContainerInterface) -> None:
        """Clear the query cache by using container type.
        This is a slightly smarter way of clearing the cache. Only queries that are of the same type (or without one)
        are cleared.
        """

        # Remove all case-insensitive matches since we won't find those with the below "<=" subset check.
        # TODO: Properly check case-insensitively in the dict's values.
        for key in list(ContainerQuery.ContainerQuery.cache):
            if not key[0]:
                del ContainerQuery.ContainerQuery.cache[key]

        # Remove all cache items that this container could fall in.
        for key in list(ContainerQuery.ContainerQuery.cache):
            query_metadata = dict(zip(key[1::2], key[2::2]))
            if query_metadata.items() <= container.getMetaData().items():
                del ContainerQuery.ContainerQuery.cache[key]

    def _onContainerMetaDataChanged(self, *args: ContainerInterface, **kwargs: Any) -> None:
        """Called when any container's metadata changed.

        This function passes it on to the containerMetaDataChanged signal. Sadly
        that doesn't work automatically between pyqtSignal and UM.Signal.
        """

        container = args[0]
        # Always emit containerMetaDataChanged, even if the dictionary didn't actually change: The contents of the dictionary might have changed in-place!
        self.metadata[container.getId()] = container.getMetaData()  # refresh the metadata
        self.containerMetaDataChanged.emit(*args, **kwargs)

    def _isMetadataValid(self, metadata: Optional[Dict[str, Any]]) -> bool:
        """Validate a metadata object.

        If the metadata is invalid, the container is not allowed to be in the
        registry.
        :param metadata: A metadata object.
        :return: Whether this metadata was valid.
        """

        return metadata is not None

    def getLockFilename(self) -> str:
        """Get the lock filename including full path
        Dependent on when you call this function, Resources.getConfigStoragePath may return different paths
        """

        return Resources.getStoragePath(Resources.Resources, self._application.getApplicationLockFilename())

    def getCacheLockFilename(self) -> str:
        """Get the cache lock filename including full path."""

        return Resources.getStoragePath(Resources.Cache, self._application.getApplicationLockFilename())

    def lockFile(self) -> LockFile:
        """Contextmanager to create a lock file and remove it afterwards."""

        return LockFile(
            self.getLockFilename(),
            timeout = 10,
            wait_msg = "Waiting for lock file in local config dir to disappear..."
            )

    def lockCache(self) -> LockFile:
        """Context manager to create a lock file for the cache directory and remove
        it afterwards.
        """

        return LockFile(
            self.getCacheLockFilename(),
            timeout = 10,
            wait_msg = "Waiting for lock file in cache directory to disappear."
        )

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
    }  # type: Dict[str, Type[ContainerInterface]]

    __instance = None  # type: ContainerRegistry

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "ContainerRegistry":
        return cls.__instance


PluginRegistry.addType("settings_container", ContainerRegistry.addContainerType)
