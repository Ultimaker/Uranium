# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import hashlib  # To generate cryptographic hashes of files.
import os  # To remove duplicate files.
import os.path  # To re-format files with their proper file extension but with a version number in between.
import shutil  # To move files in constant-time.
from typing import List, Tuple, Dict
from PyQt6.QtCore import QCoreApplication

from UM.Logger import Logger
from UM.Resources import Resources  # To get the central storage location.
from UM.Version import Version  # To track version numbers of these files.


class CentralFileStorage:
    """
    This class stores and retrieves items (files or directories) stored in a location central to all versions of the
    application. Its purpose is to provide a way for plug-ins to store big items (files or directories) without having
    those big items copied to the new resource directory at every version upgrade.

    Each items gets a path ID and a version number by which to identify the individual items. The path ID and version
    number combination needs to be unique for an item and together refer to a specific item's contents. When retrieving
    the item, the retriever needs to specify the hash of the item that it expects to find, and this hash is checked
    before giving up the location of the item. This hash will guard against unauthorised changes to the item. The
    plug-in, if properly signed, will then not be surprised by malicious content in that file or directory.

    If multiple items need to be moved, it's also possible to add a file called "central_storage.json" to the root
    directory of the plugin. This json needs to contain a list, of which each element is a list of 4 elements.
    The first element holds the relative path to the item (file or directory), the second is the ID, the third is the
    ID of the item and the last item is the hash.

    A brief example of such a file:
    [
        ["files/VeryLargeFileToStore.big", "very_large_file", "1.0.1", "abcdefghijklmnop"],
        ["relative/path/to/dir", "relative/path/to/dir/in/storage", "1.0.1, "124986978cb21e"]
    ]
    """

    # In some cases a plugin might ask for files to be moved, but it's not needed (since the plugin is actually bundled)
    # In order to ensure that the same API can still be used, we store those situations.
    _unmoved_files = {}  # type: Dict[str, str]

    _is_enterprise_version = False

    @classmethod
    def store(cls, path: str, path_id: str, version: Version = Version("1.0.0"), move_file: bool = True) -> None:
        """
        Store a new item (file or directory) into the central file storage. This item will get moved to a storage
        location that is not specific to this version of the application.

        If the item already exists, this will check if it's the same item. If the item is not the same, it raises a
        `FileExistsError`. If the item is the same, no error is raised and the item to store is simply deleted. It is a
        duplicate of the item already stored.

        Note that this function SHOULD NOT be called by plugins themselves. The central_storage.json should be used
        instead!

        :param path: The path to the item (file or directory) to store in the central file storage.
        :param path_id: A name for the item (file or directory) to store.
        :param version: A version number for the item (file or directory).
        :param move_file: Should the file be moved at all or just remembered for later retrieval
        :raises FileExistsError: There is already a centrally stored item (file or directory) with that name and
        version, but it's different.
        """
        if not move_file:
            full_identifier = path_id + str(version)
            if full_identifier not in cls._unmoved_files:
                cls._unmoved_files[full_identifier] = path
            return

        if not os.path.exists(cls.getCentralStorageLocation()):
            os.makedirs(cls.getCentralStorageLocation())
        if not os.path.exists(path):
            Logger.debug(f"{path_id} {str(version)} was already stored centrally or the provided path is not correct")
            return

        storage_path = cls._getItemPath(path_id, version)

        if os.path.exists(storage_path):  # File already exists. Check if it's the same.
            if os.path.getsize(path) != os.path.getsize(storage_path):  # As quick check if files are the same, check their file sizes.
                raise FileExistsError(f"Central file storage already has an item (file or directory) with ID {path_id} and version {str(version)}, but it's different.")
            new_item_hash = cls._hashItem(path)
            stored_item_hash = cls._hashItem(storage_path)
            if new_item_hash != stored_item_hash:
                raise FileExistsError(f"Central file storage already has an item (file or directory) with ID {path_id} and version {str(version)}, but it's different.")
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            Logger.info(f"{path_id} {str(version)} was already stored centrally. Removing duplicate.")
        else:
            shutil.move(path, storage_path)
            Logger.info(f"Storing new item {path_id}.{str(version)}.")

    @classmethod
    def retrieve(cls, path_id: str, sha256_hash: str, version: Version = Version("1.0.0")) -> str:
        """
        Retrieve the path of a previously stored item (file or directory).
        :param path_id: The name of the item (file or directory) to retrieve.
        :param sha256_hash: A SHA-256 hash of the item (file or directory) you expect to receive from the central storage.
        :param version: The version number of the item (file or directory) to retrieve.
        :return: A path to the location of the centrally stored item (file or directory).
        :raises FileNotFoundError: There is no item (file or directory) stored with that name and version.
        :raises IOError: The hash of the item (file or directory) is incorrect. Opening this item could be a security
        risk.
        """
        if path_id + str(version) in cls._unmoved_files:
            return cls._unmoved_files[path_id + str(version)]

        storage_path = cls._getItemPath(path_id, version)

        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"Central file storage doesn't have an item (file or directory) with ID {path_id} and version {str(version)}.")

        if cls._is_enterprise_version:
            stored_file_hash = cls._hashItem(storage_path)
            if stored_file_hash != sha256_hash:
                raise IOError(f"The centrally stored item (file or directory) with ID {path_id} and version {str(version)} does not match with the given hash.")

        return storage_path

    @classmethod
    def _getItemPath(cls, item_id: str, version: Version) -> str:
        """
        Get a canonical path for a hypothetical item (file or folder) with a specified ID and version.
        :param item_id: The name of the item (file or directory) to get a name for.
        :param version: The version number of the item (file or directory) to get a name for.
        :return: A path to store such an item.
        """
        item_name = item_id + "." + str(version)
        return os.path.join(cls.getCentralStorageLocation(), item_name)

    @classmethod
    def getCentralStorageLocation(cls) -> str:
        """
        Gets a directory to store things in a version-neutral location.
        :return: A directory to store things centrally.
        """
        return os.path.join(Resources.getDataStoragePath(), "..", "storage")

    @classmethod
    def _hashFile(cls, file_path: str) -> str:
        """
        Returns a SHA-256 hash of the specified file.
        :param file_path: The path to a file to get the hash of.
        :return: A cryptographic hash of the specified file.
        """
        block_size = 2 ** 16
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            contents = f.read(block_size)
            while len(contents) > 0:
                hasher.update(contents)
                contents = f.read(block_size)
        QCoreApplication.processEvents()  # Process events to allow the interface to update
        return hasher.hexdigest()

    @classmethod
    def _hashDirectory(cls, directory: str) -> str:
        """
        Returns a SHA-256 hash of the specified directory.
        :param directory: The path to a directory to get the hash of.
        :return: A cryptographic hash of the specified directory.
        """
        hash_list: List[Tuple[str, str]] = []  # Contains a list of (relative_file_path, hash) tuples
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                rel_dir_path = os.path.relpath(root, directory)
                rel_path = os.path.join(rel_dir_path, filename)
                abs_path = os.path.join(root, filename)
                hash_list.append((rel_path, cls._hashFile(abs_path)))

        ordered_list = sorted(hash_list, key = lambda x: x[0])

        hasher = hashlib.sha256()
        for i in ordered_list:
            hasher.update("".join(i).encode('utf-8'))
        return hasher.hexdigest()

    @classmethod
    def _hashItem(cls, item_path: str) -> str:
        """
        Calls the hash function according to the type of the path (directory or file).
        :param path: The path that needs to be hashed.
        :return: A cryptographic hash of the specified path.
        """
        if os.path.isdir(item_path):
            return cls._hashDirectory(item_path)
        elif os.path.isfile(item_path):
            return cls._hashFile(item_path)
        raise FileNotFoundError(f"The specified item '{item_path}' was neither a file nor a directory.")

    @classmethod
    def setIsEnterprise(cls, is_enterprise: bool) -> None:
        cls._is_enterprise_version = is_enterprise
