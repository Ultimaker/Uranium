# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import hashlib  # To generate cryptographic hashes of files.
import os  # To remove duplicate files.
import os.path  # To re-format files with their proper file extension but with a version number in between.
import shutil  # To move files in constant-time.
from typing import List, Tuple

from UM.Logger import Logger
from UM.Resources import Resources  # To get the central storage location.
from UM.Version import Version  # To track version numbers of these files.

class CentralFileStorage:
    """
    This class stores and retrieves files stored in a location central to all versions of the application. Its purpose
    is to provide a way for plug-ins to store big files without having those big files copied to the new resource
    directory at every version upgrade.

    Each file gets a file ID and a version number by which to identify the individual file. The file ID and version
    number combination needs to be unique for a file and together refer to a specific file's contents. When retrieving
    the file, the retriever needs to specify the hash of the file that it expects to find, and this hash is checked
    before giving up the location of the file. This hash will guard against unauthorised changes to the file. The
    plug-in, if properly signed, will then not be surprised by malicious content in that file.

    If multiple files need to be moved, it's also possible to add a file called "central_storage.json" to the root
    directory of the plugin. This json needs to contain a list, of which each element is a list of 4 elements.
    The first element holds the relative path to the file, the second is the ID, the third is the ID of the file and the
    last item is the hash.

    A brief example of such a file:
    [
        ["files/VeryLargeFileToStore.big", "very_large_file", "1.0.1", "abcdefghijklmnop"]
    ]
    """

    @classmethod
    def store(cls, path: str, path_id: str, version: Version = Version("1.0.0")) -> None:
        """
        Store a new file into the central file storage. This file will get moved to a storage location that is not
        specific to this version of the application.

        If the file already exists, this will check if it's the same file. If the file is not the same, it raises a
        `FileExistsError`. If the file is the same, no error is raised and the file to store is simply deleted. It is a
        duplicate of the file already stored.
        :param path: The path to the file to store in the central file storage.
        :param path_id: A name for the file to store.
        :param version: A version number for the file.
        :raises FileExistsError: There is already a centrally stored file with that name and version, but it's
        different.
        """
        if not os.path.exists(cls._centralStorageLocation()):
            os.makedirs(cls._centralStorageLocation())
        if not os.path.exists(path):
            Logger.debug(f"{path_id} {str(version)} was already stored centrally or the provided file_path is not correct")
            return

        storage_path = cls._getFilePath(path_id, version)

        if os.path.exists(storage_path):  # File already exists. Check if it's the same.
            if os.path.getsize(path) != os.path.getsize(storage_path):  # As quick check if files are the same, check their file sizes.
                raise FileExistsError(f"Central file storage already has a file with ID {path_id} and version {str(version)}, but it's different.")
            new_file_hash = cls._hashPath(path)
            stored_file_hash = cls._hashPath(storage_path)
            if new_file_hash != stored_file_hash:
                raise FileExistsError(f"Central file storage already has a file with ID {path_id} and version {str(version)}, but it's different.")
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            Logger.info(f"{path_id} {str(version)} was already stored centrally. Removing duplicate.")
        else:
            shutil.move(path, storage_path)
            Logger.info(f"Storing new file {path_id} {str(version)}.")

    @classmethod
    def retrieve(cls, path_id: str, sha256_hash: str, version: Version = Version("1.0.0")) -> str:
        """
        Retrieve the file path of a previously stored file.
        :param path_id: The name of the file or folder to retrieve.
        :param sha256_hash: A SHA-256 hash of the file or folder you expect to receive from the central storage.
        :param version: The version number of the file or folder to retrieve.
        :return: A path to the location of the centrally stored file or folder.
        :raises FileNotFoundError: There is no file stored with that name and version.
        :raises IOError: The hash of the file is incorrect. Opening this file could be a security risk.
        """
        storage_path = cls._getFilePath(path_id, version)

        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"Central file storage doesn't have a file with ID {path_id} and version {str(version)}.")
        stored_file_hash = cls._hashPath(storage_path)
        if stored_file_hash != sha256_hash:
            raise IOError(f"The centrally stored file with ID {path_id} and version {str(version)} does not match with the given file hash.")

        return storage_path

    @classmethod
    def _getFilePath(cls, file_id: str, version: Version) -> str:
        """
        Get a canonical file path for a hypothetical file with a specified ID and version.
        :param file_id: The name of the file to get a name for.
        :param version: The version number of the file to get a name for.
        :return: A path to store such a file.
        """
        file_name = file_id + "." + str(version)
        return os.path.join(cls._centralStorageLocation(), file_name)

    @classmethod
    def _centralStorageLocation(cls) -> str:
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
    def _hashPath(cls, path: str) -> str:
        """
        Calls the hash function according to the type of the path (directory or file).
        :param path: The path that needs to be hashed.
        :return: A cryptographic hash of the specified path.
        """
        if os.path.isdir(path):
            return cls._hashDirectory(path)
        elif os.path.isfile(path):
            return cls._hashFile(path)
        raise FileNotFoundError(f"The specified path '{path}' was neither a file nor a directory.")
