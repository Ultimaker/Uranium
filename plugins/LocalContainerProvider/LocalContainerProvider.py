# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys # For setrecursionlimit
import os  # For getting the IDs from a filename.
import pickle  # For caching definitions.
import re  # To detect back-up files in the ".../old/#/..." folders.
import time
import urllib.parse  # For interpreting escape characters using unquote_plus.
import gc
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from UM.Application import Application  # To get the current version for finding the cache directory.
from UM.ConfigurationErrorMessage import ConfigurationErrorMessage
from UM.Logger import Logger
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType  # To get the type of container we're loading.
from UM.Platform import Platform
from UM.Resources import Resources
from UM.SaveFile import SaveFile
from UM.Settings.ContainerProvider import ContainerProvider  # The class we're implementing.
from UM.Settings.ContainerRegistry import ContainerRegistry  # To get the resource types for containers.
from UM.Settings.DefinitionContainer import DefinitionContainer  # To check if we need to cache this container.
from UM.Settings.DefinitionContainerUnpickler import DefinitionContainerUnpickler
from UM.Version import Version  # To compare the versions of container files that share an ID.

MYPY = False
if MYPY:  # Things to import for type checking only.
    from UM.Settings.Interfaces import ContainerInterface


class LocalContainerProvider(ContainerProvider):
    """Provides containers from the local installation."""

    def __init__(self):
        """Creates the local container provider.

        This creates a cache which translates container IDs to their file names.
        """

        super().__init__()

        self._id_to_path = {}  # type: Dict[str, str] #Translates container IDs to the path to where the file is located
        self._id_to_mime = {}  # type: Dict[str, MimeType] #Translates container IDs to their MIME type.

        self._is_read_only_cache = {}  # type: Dict[str, bool]

        self._conflicting_ids = set()  # type: Set[str]  # IDs that are provided by multiple files (e.g. bundled and user-installed).

        self._storage_path = ""

    def getContainerFilePathById(self, container_id: str) -> Optional[str]:
        return self._id_to_path.get(container_id)

    def getAllIds(self) -> Iterable[str]:
        """Gets the IDs of all local containers.

        :return: A sequence of all container IDs.
        """

        if not self._id_to_path:
            self._updatePathCache()
        return self._id_to_path.keys()

    def getLastModifiedTime(self, container_id: str) -> float:
        if container_id in self._conflicting_ids:
            # Which of the files is used can change between runs without the used file itself being modified (for
            # instance when a newer version is bundled with the application). The cached metadata could then belong to
            # a different file, so make sure that it is always refreshed.
            return time.time()
        try:
            return os.path.getmtime(self._id_to_path[container_id])
        except OSError:  # File system can be corrupt.
            return time.time()  # Pretend it just got modified.

    def loadContainer(self, container_id: str) -> "ContainerInterface":
        # First get the actual (base) ID of the path we're going to read.
        file_path = self._id_to_path[container_id]  # Raises KeyError if container ID does not exist in the (cache of the) files.
        base_id = self._pathToId(file_path)
        if not base_id:
            raise Exception(f"The file where container {container_id} supposedly comes from is not a container file.")

        container = None  # type: Optional[ContainerInterface]

        container_class = ContainerRegistry.mime_type_map[self._id_to_mime[base_id].name]
        if issubclass(container_class, DefinitionContainer):  # We may need to load these from the definition cache.
            container = self._loadCachedDefinition(container_id)
            if container:   # Yes, it was cached!
                return container

        # Not cached, so load by deserialising.
        container = container_class(base_id)
        with open(file_path, "r", encoding = "utf-8") as f:
            container.deserialize(f.read(), file_path)
        container.setPath(file_path)

        if isinstance(container, DefinitionContainer):
            self._saveCachedDefinition(container)

        if base_id == container_id:
            return container
        # If we're not requesting the base ID, the sub-container must have been side loaded.
        return ContainerRegistry.getInstance().findContainers(id = container_id)[0]

    def saveContainer(self, container: "ContainerInterface") -> None:
        """Find out where to save a container and save it there"""

        try:
            data = container.serialize()
        except NotImplementedError:
            return
        except Exception:
            Logger.logException("e", f"An exception occurred when serializing container {container.getId()}")
            return

        mime_type = ContainerRegistry.getMimeTypeForContainer(type(container))
        if mime_type is None:
            Logger.warning(f"Failed to get MIME type for container type [{type(container)}]")
            return
        file_name = urllib.parse.quote_plus(container.getId()) + "." + mime_type.preferredSuffix
        container_type = container.getMetaDataEntry("type")
        resource_types = ContainerRegistry.getInstance().getResourceTypes()
        if container_type in resource_types:
            path = Resources.getStoragePath(resource_types[container_type], file_name)
            try:
                with SaveFile(path, "wt") as f:
                    f.write(data)
            except OSError as e:
                Logger.error(f"Unable to store local container to path {path}: {e}")
                return
            container.setPath(path)
            # Register it internally as being saved
            self._id_to_path[container.getId()] = path
            mime = self._pathToMime(path)
            if mime is not None:
                self._id_to_mime[container.getId()] = mime
            else:
                Logger.error(f"Failed to find MIME type for container ID [{container.getId()}] with path [{path}]")

            base_file = container.getMetaData().get("base_file")
            if base_file:
                for container_md in ContainerRegistry.getInstance().findContainersMetadata(base_file = base_file):
                    self._id_to_path[container_md["id"]] = path
                    mime = self._pathToMime(path)
                    if mime is not None:
                        self._id_to_mime[container_md["id"]] = mime
                    else:
                        Logger.error(f"Failed to find MIME type for container ID [{container.getId()}] with path [{path}]")
        else:
            Logger.warning(f"Dirty container [{container.getId()}] is not saved because the resource type [{container_type}] is unknown in ContainerRegistry")

    def loadMetadata(self, container_id: str) -> Dict[str, Any]:
        """Load the metadata of a specified container.

        :param container_id: The ID of the container to load the metadata of.
        :return: The metadata of the specified container, or `None` if the
                 metadata failed to load.
        """

        registry = ContainerRegistry.getInstance()
        if container_id in registry.metadata:
            return registry.metadata[container_id]

        filename = self._id_to_path[container_id]  # Raises KeyError if container ID does not exist in the (cache of the) files!
        clazz = ContainerRegistry.mime_type_map[self._id_to_mime[container_id].name]

        requested_metadata = {}  # type: Dict[str, Any]
        try:
            with open(filename, "r", encoding = "utf-8") as f:
                result_metadatas = clazz.deserializeMetadata(f.read(), container_id) #pylint: disable=no-member
        except IOError as e:
            Logger.error(f"Unable to load metadata from file {filename}: {e}")
            ConfigurationErrorMessage.getInstance().addFaultyContainers(container_id)
            return {}
        except Exception as e:
            Logger.logException("e", f"Unable to deserialize metadata for container {filename}: {container_id}: {e}")
            ConfigurationErrorMessage.getInstance().addFaultyContainers(container_id)
            return {}

        for metadata in result_metadatas:
            if "id" not in metadata:
                Logger.warning(f"Metadata obtained from deserializeMetadata of {clazz.__name__} didn't contain an ID.")
                continue
            if metadata["id"] == container_id:
                requested_metadata = metadata
            # Side-load the metadata into the registry if we get multiple containers.
            if metadata["id"] not in registry.metadata:  # This wouldn't get loaded normally.
                self._id_to_path[metadata["id"]] = filename
                self._id_to_mime[metadata["id"]] = self._id_to_mime[container_id]  # Assume that they only return one MIME type.
                registry.metadata[metadata["id"]] = metadata
                registry.source_provider[metadata["id"]] = self
        return requested_metadata

    def isReadOnly(self, container_id: str) -> bool:
        """Returns whether a container is read-only or not.

        A container can only be modified if it is stored in the data directory.
        :return: Whether the specified container is read-only.
        """

        if container_id in self._is_read_only_cache:
            return self._is_read_only_cache[container_id]
        if self._storage_path == "":
            try:
                self._storage_path = os.path.realpath(Resources.getDataStoragePath())
            except OSError:  # Directory can't be accessed.
                self._is_read_only_cache[container_id] = True
                return True
        storage_path = self._storage_path

        file_path = self._id_to_path[container_id]  # If KeyError: We don't know this ID.

        # The container is read-only if file_path is not a subdirectory of storage_path.
        if Platform.isWindows():
            # On Windows, if the paths provided to commonpath() don't come from the same drive,
            # a ValueError will be raised.
            try:
                result = os.path.commonpath([storage_path, os.path.realpath(file_path)]) != storage_path
            except ValueError:
                result = True
        else:
            result = os.path.commonpath([storage_path, os.path.realpath(file_path)]) != storage_path

        result |= ContainerRegistry.getInstance().isExplicitReadOnly(container_id)
        self._is_read_only_cache[container_id] = result
        return result

    def removeContainer(self, container_id: str) -> None:
        """Remove or unregister an id."""

        if container_id not in self._id_to_path:
            Logger.warning(f"Tried to remove unknown container: {container_id}")
            return
        path_to_delete = self._id_to_path[container_id]
        del self._id_to_path[container_id]
        del self._id_to_mime[container_id]

        # Remove file related to a container
        #
        # Since we cannot assume we can write to any other path, we can only support removing from
        # a storage path. This effectively "resets" a container that is located in another resource
        # path.
        try:
            if os.path.isfile(path_to_delete):
                Logger.info(f"Deleting file {path_to_delete}.")
                os.remove(path_to_delete)
        except Exception:
            Logger.warning(f"Tried to delete file [{path_to_delete}], but it failed")

    def _loadCachedDefinition(self, definition_id) -> Optional[DefinitionContainer]:
        """Load a pre-parsed definition container.

        Definition containers can be quite expensive to load, so this loads a
        pickled version of the definition if one is available.

        :param definition_id: The ID of the definition to load from the cache.
        :return: If a cached version was available, return it. If not, return
                 ``None``.
        """

        definition_path = self._id_to_path[definition_id]
        try:
            cache_path = Resources.getPath(Resources.Cache, "definitions", Application.getInstance().getVersion(), definition_id)
            cache_mtime = os.path.getmtime(cache_path)
            definition_mtime = os.path.getmtime(definition_path)
        except FileNotFoundError:  # Cache doesn't exist yet.
            return None
        except PermissionError:  # No read permission.
            return None

        if definition_mtime > cache_mtime:
            # The definition is newer than the cached version, so ignore the cached version.
            Logger.debug(f"Definition file {definition_path} is newer than cache. Ignoring cached version.")
            return None

        try:
            gc.disable()
            with open(cache_path, "rb") as f:
                # The DefinitionContainerUnpickler has a list of whitelisted globals
                definition = DefinitionContainerUnpickler(f).load()
        except (OSError, PermissionError, IOError, AttributeError, EOFError, ImportError, IndexError, pickle.UnpicklingError) as e:
            Logger.warning(f"Failed to load definition {definition_id} from cached file: {e}")
            return None
        finally:
            gc.enable()

        try:
            for file_path in definition.getInheritedFiles():
                if os.path.getmtime(file_path) > cache_mtime:
                    return None
        except FileNotFoundError:
            return None  # Cache for parent doesn't exist yet.

        return definition

    def _saveCachedDefinition(self, definition: DefinitionContainer) -> None:
        """Cache a definition container on disk.

        Definition containers can be quite expensive to parse and load, so this
        pickles a container and saves the pre-parsed definition on disk.

        :param definition: The definition container to store.
        """

        cache_path = Resources.getStoragePath(Resources.Cache, "definitions", Application.getInstance().getVersion(), definition.id)

        # Ensure the cache path exists.
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok = True)
        except PermissionError:
            Logger.warning(f"The definition cache for definition {definition.getId()} failed to save because you don't have permissions to write in the cache directory.")
            return  # No rights to save it. Better give up.

        recursionlimit = sys.getrecursionlimit()
        sys.setrecursionlimit(3000)
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(definition, f, pickle.HIGHEST_PROTOCOL)
        except RecursionError:
            # Sometimes a recursion error in pickling occurs here.
            # The cause is unknown. It must be some circular reference in the definition instances or definition containers.
            # Instead of saving a partial cache and raising an exception, simply fail to save the cache.
            # See CURA-4024.
            Logger.warning(f"The definition cache for definition {definition.getId()} failed to pickle.")
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)  # The pickling might be half-complete, which causes EOFError in Pickle when you load it later.
                except PermissionError:
                    # Someone else is touching this file.
                    Logger.warning(f"Unable to remove picked file as another process has access to it {cache_path}")
        except PermissionError:
            Logger.warning(f"Cura didn't get permission to save the definition {definition.getId()}")
        finally:
            sys.setrecursionlimit(recursionlimit)

    def _updatePathCache(self) -> None:
        """Updates the cache of paths to containers.

        This way we can more easily load the container files we want lazily.
        """

        self._id_to_path = {}  # Clear cache first.
        self._id_to_mime = {}
        self._conflicting_ids = set()

        old_file_expression = re.compile(r"\{sep}old\{sep}\d+\{sep}".format(sep = os.sep))  # To detect files that are back-ups. Matches on .../old/#/...

        # Collect all files that provide each container ID, in order of priority. The same container can be available
        # in several locations, for instance bundled with the application and in the user's configuration folder.
        candidates = {}  # type: Dict[str, List[Tuple[str, MimeType]]]
        for resource_type in ContainerRegistry.getInstance().getResourceTypes().values():
            for paths in Resources.getAllResourceCandidatesOfType(resource_type).values():
                for filename in paths:
                    if re.search(old_file_expression, filename):
                        continue  # This is a back-up file from an old version.

                    container_id, mime = self._pathToIdAndMime(filename)
                    if not container_id:
                        continue
                    if not mime:
                        continue
                    container_candidates = candidates.setdefault(container_id, [])
                    if all(path != filename for path, _ in container_candidates):
                        container_candidates.append((filename, mime))

        for container_id, container_candidates in candidates.items():
            if len(container_candidates) > 1:
                self._conflicting_ids.add(container_id)
            filename, mime = self._selectNewestCandidate(container_id, container_candidates)
            self._id_to_path[container_id] = filename
            self._id_to_mime[container_id] = mime

    def _selectNewestCandidate(self, container_id: str, candidates: List[Tuple[str, MimeType]]) -> Tuple[str, MimeType]:
        """Selects which of the files providing a container is the one that should be used.

        The file with the highest version wins. If versions are equal, the file with the highest priority wins, i.e. the
        one in the user's storage location before the ones that are bundled with the application.

        :param container_id: The ID of the container that all candidates provide.
        :param candidates: The paths and MIME types of the files providing the container, ordered by priority.
        :return: The path and MIME type of the file to use.
        """

        best = candidates[0]
        if len(candidates) == 1:
            return best

        best_version = self._getContainerVersion(container_id, best[0], best[1])
        for candidate in candidates[1:]:
            version = self._getContainerVersion(container_id, candidate[0], candidate[1])
            if version > best_version:
                best = candidate
                best_version = version
        Logger.debug(f"Container {container_id} is provided by multiple files. Using {best[0]} (version {best_version}).")
        return best

    @staticmethod
    def _getContainerVersion(container_id: str, path: str, mime: MimeType) -> Version:
        """Reads the version of a container from its file.

        :return: The version in the metadata of the container, or version 0 if it has none or can't be read.
        """

        container_class = ContainerRegistry.mime_type_map[mime.name]
        try:
            with open(path, "r", encoding = "utf-8") as f:
                all_metadata = container_class.deserializeMetadata(f.read(), container_id)  #pylint: disable=no-member
        except Exception as e:
            Logger.warning(f"Unable to read the version of container {container_id} from {path}: {e}")
            return Version("0")

        for metadata in all_metadata:
            if metadata.get("id") == container_id:
                return Version(str(metadata.get("version", "0")))
        return Version("0")

    @staticmethod
    def _pathToIdAndMime(path: str) -> Tuple[Optional[str], Optional[MimeType]]:
        """ Faster combination of _pathToMime and _pathToID

            When we want to know the mime and the ID, it's better to use this function, as this prevents an extra
            mime detection from having to be made.
        """
        try:
            mime = MimeTypeDatabase.getMimeTypeForFile(path)
        except MimeTypeDatabase.MimeTypeNotFoundError:
            Logger.warning(f"MIME type could not be found for file: {path}, ignoring it.")
            return None, None
        if mime.name not in ContainerRegistry.mime_type_map:  # The MIME type is known, but it's not a container.
            return None, None
        recovered_id = None
        if mime:
            recovered_id = urllib.parse.unquote_plus(mime.stripExtension(os.path.basename(path)))
        return recovered_id, mime

    @staticmethod
    def _pathToMime(path: str) -> Optional[MimeType]:
        """Converts a file path to the MIME type of the container it represents.

        :return: The MIME type or None if it's not a container.
        """

        try:
            mime = MimeTypeDatabase.getMimeTypeForFile(path)
        except MimeTypeDatabase.MimeTypeNotFoundError:
            Logger.warning(f"MIME type could not be found for file: {path}, ignoring it.")
            return None
        if mime.name not in ContainerRegistry.mime_type_map:  # The MIME type is known, but it's not a container.
            return None
        return mime

    @staticmethod
    def _pathToId(path: str) -> Optional[str]:
        """Converts a file path to the ID of the container it represents."""

        result = None
        mime = LocalContainerProvider._pathToMime(path)
        if mime:
            result = urllib.parse.unquote_plus(mime.stripExtension(os.path.basename(path)))
        return result
