# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import hashlib  # To generate cryptographic hashes of files.
import os  # To remove duplicate files.
import os.path  # To re-format files with their proper file extension but with a version number in between.
import shutil  # To move files in constant-time.

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
    """

    @classmethod
    def store(cls, file_path: str, file_id: str, version: Version = Version("1.0.0")) -> None:
        """
        Store a new file into the central file storage. This file will get moved to a storage location that is not
        specific to this version of the application.

        If the file already exists, this will check if it's the same file. If the file is not the same, it raises a
        `FileExistsError`. If the file is the same, no error is raised and the file to store is simply deleted. It is a
        duplicate of the file already stored.
        :param file_path: The path to the file to store in the central file storage.
        :param file_id: A name for the file to store.
        :param version: A version number for the file.
        """
        if not os.path.exists(file_path):
            return
        storage_path = cls._getFilePath(file_id, version)

        if os.path.exists(storage_path):  # File already exists. Check if it's the same.
            new_file_hash = cls._hashFile(file_path)
            stored_file_hash = cls._hashFile(storage_path)
            if new_file_hash != stored_file_hash:
                raise FileExistsError(f"Central file storage already has a file with ID {file_id} and version {str(version)}, but it's different.")
            os.remove(file_path)
        else:
            shutil.move(file_path, storage_path)

    @classmethod
    def retrieve(cls, file_id: str, sha256_hash: str, version: Version = Version("1.0.0")) -> str:
        """
        Retrieve the file path of a previously stored file.
        :param file_id: The name of the file to retrieve.
        :param sha256_hash: A SHA-256 hash of the file you expect to receive from the central storage.
        :param version: The version number of the file to retrieve.
        :return: A path to the location of the centrally stored file.
        """
        storage_path = cls._getFilePath(file_id, version)

        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"Central file storage doesn't have a file with ID {file_id} and version {str(version)}.")
        stored_file_hash = cls._hashFile(storage_path)
        if stored_file_hash != sha256_hash:
            raise IOError(f"The centrally stored file with ID {file_id} and version {str(version)} does not match with the given file hash.")

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
        return os.path.join(Resources.getDataStoragePath(), "..", "storage", file_name)

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
