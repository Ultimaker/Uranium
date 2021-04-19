# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Version import Version

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
        pass  # TODO.

    @classmethod
    def retrieve(cls, file_id: str, sha256_hash: str, version: Version = Version("1.0.0")) -> str:
        """
        Retrieve the file path of a previously stored file.
        :param file_id: The name of the file to retrieve.
        :param sha256_hash: A SHA-256 hash of the file you expect to receive from the central storage.
        :param version: The version number of the file to retrieve.
        :return: A path to the location of the centrally stored file.
        """
        pass  # TODO.