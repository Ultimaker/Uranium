# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os
import re #For finding containers with asterisks in the constraints and for detecting backup files.
import urllib #For ensuring container file names are proper file names
import urllib.parse
import pickle #For serializing/deserializing Python classes to binary files
from typing import List, Optional, cast
import collections
import time

import UM.FlameProfiler
from UM.PluginRegistry import PluginRegistry
from UM.Resources import Resources, UnsupportedStorageTypeError
from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Logger import Logger
from UM.SaveFile import SaveFile
from UM.Settings.Interfaces import ContainerInterface
from UM.Signal import Signal, signalemitter
from UM.LockFile import LockFile

import UM.Dictionary

MYPY = False
if MYPY:
    from UM.Application import Application

from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.Interfaces import ContainerRegistryInterface
from UM.Settings.Interfaces import DefinitionContainerInterface

from . import ContainerQuery

CONFIG_LOCK_FILENAME = "uranium.lock"

# The maximum amount of query results we should cache
MaxQueryCacheSize = 1000

##  Central class to manage all Setting containers.
#
#
@signalemitter
class ContainerRegistry(ContainerRegistryInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._emptyInstanceContainer = _EmptyInstanceContainer("empty")

        self._containers = [self._emptyInstanceContainer]   # type: List[ContainerInterface]
        self._id_container_cache = {}
        self._resource_types = [Resources.DefinitionContainers] # type: List[int]
        self._query_cache = collections.OrderedDict() # This should really be an ordered set but that does not exist...

        #Since queries are based on metadata, we need to make sure to clear the cache when a container's metadata changes.
        self.containerMetaDataChanged.connect(self._clearQueryCache)

    containerAdded = Signal()
    containerRemoved = Signal()
    containerMetaDataChanged = Signal()

    def addResourceType(self, type: int) -> None:
        self._resource_types.append(type)

    ##  Find all DefinitionContainer objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the
    #   DefinitionContainer. An asterisk in the values can be used to denote a
    #   wildcard.
    def findDefinitionContainers(self, **kwargs) -> List[DefinitionContainerInterface]:
        return cast(List[DefinitionContainerInterface], self.findContainers(DefinitionContainer, **kwargs))

    ##  Find all InstanceContainer objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the
    #   InstanceContainer. An asterisk in the values can be used to denote a
    #   wildcard.
    def findInstanceContainers(self, **kwargs) -> List[InstanceContainer]:
        return cast(List[InstanceContainer], self.findContainers(InstanceContainer, **kwargs))

    ##  Find all ContainerStack objects matching certain criteria.
    #
    #   \param kwargs \type{dict} A dictionary of keyword arguments containing
    #   keys and values that need to match the metadata of the ContainerStack.
    #   An asterisk in the values can be used to denote a wildcard.
    def findContainerStacks(self, **kwargs) -> List[ContainerStack]:
        return cast(List[ContainerStack], self.findContainers(ContainerStack, **kwargs))

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
    @UM.FlameProfiler.profile
    def findContainers(self, container_type = None, *, ignore_case = False, **kwargs) -> List[ContainerInterface]:
        # Create the query object
        query = ContainerQuery.ContainerQuery(self, container_type, ignore_case = ignore_case, **kwargs)

        if query.isIdOnly():
            # If we are just searching for a single container by ID, look it up from the ID-based cache
            container = self._id_container_cache.get(kwargs.get("id"))
            if container:
                # Add an extra check to make sure the found container matches the requested container type.
                # This should never occur but has happened with broken configurations.
                if not container_type:
                    return [ container ]
                elif isinstance(container, container_type):
                    return [ container ]

        if query in self._query_cache:
            # If the exact same query is in the cache, we can re-use the query result
            self._query_cache.move_to_end(query) # Query was used, so make sure to update its position
            return self._query_cache[query].getResult()

        # Execute the query, then add it to the cache
        query.execute()
        self._query_cache[query] = query

        if len(self._query_cache) > MaxQueryCacheSize:
            # Since we use an OrderedDict, we can use a simple FIFO scheme
            # to discard queries. As long as we properly update queries
            # that are being used, this results in the least used queries
            # to be discarded.
            self._query_cache.popitem(last = False)

        return query.getResult()

    ##  This is a small convenience to make it easier to support complex structures in ContainerStacks.
    def getEmptyInstanceContainer(self) -> InstanceContainer:
        return self._emptyInstanceContainer

    ##  Load all available definition containers, instance containers and
    #   container stacks.
    #
    #   \note This method does not clear the internal list of containers. This means that any containers
    #   that were already added when the first call to this method happened will not be re-added.
    def load(self) -> None:
        files = []
        old_file_expression = re.compile(r"\{sep}old\{sep}\d+\{sep}".format(sep = os.sep))

        for resource_type in self._resource_types:
            resources = Resources.getAllResourcesOfType(resource_type)

            try:
                resource_storage_path = Resources.getStoragePathForType(resource_type)
            except UnsupportedStorageTypeError:
                resource_storage_path = ""

            # Pre-process the list of files to insert relevant data
            # Most importantly, we need to ensure the loading order is DefinitionContainer, InstanceContainer, ContainerStack
            for path in resources:
                if old_file_expression.search(path):
                    # This is a backup file, ignore it.
                    continue

                try:
                    mime = MimeTypeDatabase.getMimeTypeForFile(path)
                except MimeTypeDatabase.MimeTypeNotFoundError:
                    # No valid mime type found for file, ignore it.
                    continue

                container_type = self.__mime_type_map.get(mime.name)
                if not container_type:
                    Logger.log("w", "Could not determine container type for file %s, ignoring", path)
                    continue

                type_priority = container_type.getLoadingPriority()

                # Since we have the mime type and resource type here, process these two properties so we do not
                # need to look up mime types etc. again.
                container_id = urllib.parse.unquote_plus(mime.stripExtension(os.path.basename(path)))
                read_only = os.path.realpath(os.path.dirname(path)) != os.path.realpath(resource_storage_path)

                files.append((type_priority, container_id, path, read_only, container_type))

        # Sort the list of files by type_priority so we can ensure correct loading order.
        files = sorted(files, key = lambda i: i[0])
        resource_start_time = time.time()
        with self.lockCache(): #Because we might be writing cache files.
            for _, container_id, file_path, read_only, container_type in files:
                if container_id in self._id_container_cache:
                    Logger.log("c", "Found a container with a duplicate ID: %s", container_id)
                    Logger.log("c", "Existing container is %s, trying to load %s from %s", self._id_container_cache[container_id], container_type, file_path)
                    continue

                try:
                    if issubclass(container_type, DefinitionContainer):
                        definition = self._loadCachedDefinition(container_id, file_path)
                        if definition:
                            self.addContainer(definition)
                            continue

                    new_container = container_type(container_id)
                    with open(file_path, encoding = "utf-8") as f:
                        new_container.deserialize(f.read())
                    new_container.setReadOnly(read_only)
                    new_container.setPath(file_path)

                    if issubclass(container_type, DefinitionContainer):
                        self._saveCachedDefinition(new_container)

                    self.addContainer(new_container)
                except Exception as e:
                    Logger.logException("e", "Could not deserialize container %s", container_id)
            Logger.log("d", "Loading data into container registry took %s seconds", time.time() - resource_start_time)

    @UM.FlameProfiler.profile
    def addContainer(self, container: ContainerInterface) -> None:
        containers = self.findContainers(container_type = container.__class__, id = container.getId())
        if containers:
            Logger.log("w", "Container of type %s and id %s already added", repr(container.__class__), container.getId())
            return

        if hasattr(container, "metaDataChanged"):
            container.metaDataChanged.connect(self._onContainerMetaDataChanged)

        self._containers.append(container)
        self._id_container_cache[container.getId()] = container
        self._clearQueryCache()
        self.containerAdded.emit(container)

    @UM.FlameProfiler.profile
    def removeContainer(self, container_id: str) -> None:
        containers = self.findContainers(None, id = container_id)
        if containers:
            container = containers[0]

            self._containers.remove(container)
            if container.getId() in self._id_container_cache:
                del self._id_container_cache[container.getId()]
            self._deleteFiles(container)

            if hasattr(container, "metaDataChanged"):
                container.metaDataChanged.disconnect(self._onContainerMetaDataChanged)

            self._clearQueryCache()
            self.containerRemoved.emit(container)

            Logger.log("d", "Removed container %s", container.getId())

        else:
            Logger.log("w", "Could not remove container with id %s, as no container with that ID is known", container_id)

    @UM.FlameProfiler.profile
    def renameContainer(self, container_id, new_name, new_id = None):
        Logger.log("d", "Renaming container %s to %s", container_id, new_name)
        containers = self.findContainers(None, id = container_id)
        if not containers:
            Logger.log("w", "Unable to rename container %s, because it does not exist", container_id)
            return

        container = containers[0]

        if new_name == container.getName():
            Logger.log("w", "Unable to rename container %s, because the name (%s) didn't change", container_id, new_name)
            return

        # Remove all files relating to the old container
        self._deleteFiles(container)
        self.containerRemoved.emit(container)

        container.setName(new_name)
        if new_id:
            del self._id_container_cache[container._id]
            container._id = new_id
            self._id_container_cache[container._id] = container # Keep cache up-to-date.

        self._clearQueryCache()
        self.containerAdded.emit(container)

    def saveAll(self) -> None:
        for instance in self.findInstanceContainers():
            if not instance.isDirty():
                continue

            try:
                data = instance.serialize()
            except NotImplementedError:
                # Serializing is not supported so skip this container
                continue
            except Exception:
                Logger.logException("e", "An exception occurred trying to serialize container %s", instance.getId())
                continue

            mime_type = self.getMimeTypeForContainer(type(instance))
            if mime_type is not None:
                file_name = urllib.parse.quote_plus(instance.getId()) + "." + mime_type.preferredSuffix
                path = Resources.getStoragePath(Resources.InstanceContainers, file_name)
                with SaveFile(path, "wt") as f:
                    f.write(data)

        for stack in self.findContainerStacks():
            if not stack.isDirty():
                continue

            try:
                data = stack.serialize()
            except NotImplementedError:
                # Serializing is not supported so skip this container
                continue
            except Exception:
                Logger.logException("e", "An exception occurred trying to serialize container %s", stack.getId())
                continue

            mime_type = self.getMimeTypeForContainer(type(stack))
            if mime_type is not None:
                file_name = urllib.parse.quote_plus(stack.getId()) + "." + mime_type.preferredSuffix
                path = Resources.getStoragePath(Resources.ContainerStacks, file_name)
                with SaveFile(path, "wt") as f:
                    f.write(data)

        for definition in self.findDefinitionContainers():
            try:
                data = definition.serialize()
            except NotImplementedError:
                # Serializing is not supported so skip this container
                continue
            except Exception:
                Logger.logException("e", "An exception occurred trying to serialize container %s", definition.getId())
                continue

            mime_type = self.getMimeTypeForContainer(type(definition))
            if mime_type is not None:
                file_name = urllib.parse.quote_plus(definition.getId()) + "." + mime_type.preferredSuffix
                path = Resources.getStoragePath(Resources.DefinitionContainers, file_name)
                with SaveFile(path, "wt") as f:
                    f.write(data)

    ##  Creates a new unique name for a container that doesn't exist yet.
    #
    #   It tries if the original name you provide exists, and if it doesn't
    #   it'll add a " #1" or " #2" after the name to make it unique.
    #
    #   \param original The original name that may not be unique.
    #   \return A unique name that looks a lot like the original but may have
    #   a number behind it to make it unique.
    def uniqueName(self, original: str) -> str:
        name = original.strip()

        num_check = re.compile(r"(.*?)\s*#\d+$").match(name)
        if num_check: #There is a number in the name.
            name = num_check.group(1) #Filter out the number.

        if not name: #Wait, that deleted everything!
            name = "Profile"
        elif not self.findContainers(id = original.strip(), ignore_case = True) and not self.findContainers(name = original.strip()):
            # Check if the stripped version of the name is unique (note that this can still have the number in it)
            return original.strip()

        unique_name = name
        i = 1
        while self.findContainers(id = unique_name, ignore_case = True) or self.findContainers(name = unique_name): #A container already has this name.
            i += 1 #Try next numbering.
            unique_name = "%s #%d" % (name, i) #Fill name like this: "Extruder #2".
        return unique_name

    ##  Add a container type that will be used to serialize/deserialize containers.
    #
    #   \param container An instance of the container type to add.
    @classmethod
    def addContainerType(cls, container):
        plugin_id = container.getPluginId()
        metadata = PluginRegistry.getInstance().getMetaData(plugin_id)
        if "settings_container" not in metadata or "mimetype" not in metadata["settings_container"]:
            raise Exception("Plugin {plugin} has incorrect metadata: Expected a 'settings_container' block with a 'mimetype' entry".format(plugin = plugin_id))
        cls.addContainerTypeByName(container.__class__, plugin_id, metadata["settings_container"]["mimetype"])

    ##  Used to associate mime types with object to be created
    #   \param container_type  ContainerStack or derivative
    #   \param type_name
    #   \param mime_type
    @classmethod
    def addContainerTypeByName(cls, container_type, type_name, mime_type):
        cls.__container_types[type_name] = container_type
        cls.__mime_type_map[mime_type] = container_type

    ##  Retrieve the mime type corresponding to a certain container type
    #
    #   \param container_type The type of container to get the mime type for.
    #
    #   \return A MimeType object that matches the mime type of the container or None if not found.
    @classmethod
    def getMimeTypeForContainer(cls, container_type):
        try:
            mime_type_name = UM.Dictionary.findKey(cls.__mime_type_map, container_type)
            if mime_type_name:
                return MimeTypeDatabase.getMimeType(mime_type_name)
        except ValueError:
            Logger.log("w", "Unable to find mimetype for container %s", container_type)
        return None

    ##  Get the container type corresponding to a certain mime type.
    #
    #   \param mime_type The mime type to get the container type for.
    #
    #   \return A class object of a container type that corresponds to the specified mime type or None if not found.
    @classmethod
    def getContainerForMimeType(cls, mime_type):
        return cls.__mime_type_map.get(mime_type.name, None)

    ##  Get all the registered container types
    #
    #   \return A dictionary view object that provides access to the container types.
    #           The key is the plugin ID, the value the container type.
    @classmethod
    def getContainerTypes(cls):
        return cls.__container_types.items()

    # Remove all files related to a container located in a storage path
    #
    # Since we cannot assume we can write to any other path, we can only support removing from
    # a storage path. This effectively "resets" a container that is located in another resource
    # path.
    def _deleteFiles(self, container):
        for resource_type in self._resource_types:
            mime_type_name = ""
            for name, container_type in self.__mime_type_map.items():
                if container_type == container.__class__:
                    mime_type_name = name
                    break
            else:
                return

            mime_type = MimeTypeDatabase.getMimeType(mime_type_name)

            for suffix in mime_type.suffixes:
                try:
                    path = Resources.getStoragePath(resource_type, urllib.parse.quote_plus(container.getId()) + "." + suffix)
                    if os.path.isfile(path):
                        os.remove(path)
                except Exception:
                    continue

    # Load a binary cached version of a DefinitionContainer
    def _loadCachedDefinition(self, definition_id, path):
        try:
            cache_path = Resources.getPath(Resources.Cache, "definitions", self.getApplication().getVersion(), definition_id)

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

    # Store a cached version of a DefinitionContainer
    def _saveCachedDefinition(self, definition):
        cache_path = Resources.getStoragePath(Resources.Cache, "definitions", self.getApplication().getVersion(), definition.id)

        # Ensure the cache path exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(definition, f)
        except RecursionError:
            #Sometimes a recursion error in pickling occurs here.
            #The cause is unknown. It must be some circular reference in the definition instances or definition containers.
            #Instead of saving a partial cache and raising an exception, simply fail to save the cache.
            #See CURA-4024.
            Logger.log("w", "The definition cache for definition {definition_id} failed to pickle.".format(definition_id = definition.getId()))
            if os.path.exists(cache_path):
                os.remove(cache_path) #The pickling might be half-complete, which causes EOFError in Pickle when you load it later.

    # Clear the internal query cache
    def _clearQueryCache(self, *args, **kwargs):
        self._query_cache.clear()

    ##  Called when any container's metadata changed.
    #
    #   This function passes it on to the containerMetaDataChanged signal. Sadly
    #   that doesn't work automatically between pyqtSignal and UM.Signal.
    def _onContainerMetaDataChanged(self, *args, **kwargs):
        self.containerMetaDataChanged.emit(*args, **kwargs)

    ##  Get the lock filename including full path
    #   Dependent on when you call this function, Resources.getConfigStoragePath may return different paths
    def getLockFilename(self):
        return Resources.getStoragePath(Resources.Resources, CONFIG_LOCK_FILENAME)

    ##  Get the cache lock filename including full path.
    def getCacheLockFilename(self):
        return Resources.getStoragePath(Resources.Cache, CONFIG_LOCK_FILENAME)

    ##  Contextmanager to create a lock file and remove it afterwards.
    def lockFile(self):
        return LockFile(
            self.getLockFilename(),
            timeout = 10,
            wait_msg = "Waiting for lock file in local config dir to disappear..."
            )

    ##  Context manager to create a lock file for the cache directory and remove
    #   it afterwards.
    def lockCache(self):
        return LockFile(
            self.getCacheLockFilename(),
            timeout = 10,
            wait_msg = "Waiting for lock file in cache directory to disappear."
        )

    ##  Get the singleton instance for this class.
    @classmethod
    def getInstance(cls) -> "ContainerRegistry":
        # Note: Explicit use of class name to prevent issues with inheritance.
        if not ContainerRegistry.__instance:
            ContainerRegistry.__instance = cls()
        return ContainerRegistry.__instance

    @classmethod
    def setApplication(cls, application):
        cls.__application = application

    @classmethod
    def getApplication(cls):
        return cls.__application

    __application = None    # type: Application
    __instance = None  # type: ContainerRegistry

    __container_types = {
        "definition": DefinitionContainer,
        "instance": InstanceContainer,
        "stack": ContainerStack,
    }

    __mime_type_map = {
        "application/x-uranium-definitioncontainer": DefinitionContainer,
        "application/x-uranium-instancecontainer": InstanceContainer,
        "application/x-uranium-containerstack": ContainerStack,
        "application/x-uranium-extruderstack": ContainerStack
    }

PluginRegistry.addType("settings_container", ContainerRegistry.addContainerType)


class _EmptyInstanceContainer(InstanceContainer):
    def isDirty(self) -> bool:
        return False

    def isReadOnly(self) -> bool:
        return True

    def getProperty(self, key, property_name, context = None):
        return None

    def setProperty(self, key, property_name, property_value, container = None, set_from_cache = False):
        Logger.log("e", "Setting property %s of container %s which should remain empty", key, self.getName())
        return

    def getConfigurationType(self) -> str:
        return ""  # FIXME: not sure if this is correct

    def serialize(self, ignored_metadata_keys: Optional[List] = None) -> str:
        return "[general]\n version = 2\n name = empty\n definition = fdmprinter\n"
