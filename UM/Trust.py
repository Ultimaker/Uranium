# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import base64
import json
import os
from typing import Callable, Optional, Tuple

# Note that we unfortunately need to use 'hazmat' code, as there apparently is no way to do what we want otherwise.
# (Even if what we want should be relatively commonplace in security.)
# Noted because if we _can_ make the change away from 'hazmat' (as opposed to lib-cryptography in general) we _should_.
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey, RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

from UM.Logger import Logger
from UM.Resources import Resources


class TrustBasics:
    """Anything shared between the main code and the (keygen/signing) scripts which does not need state.

    See 'Trust' (below) and the 'createkeypair.py', 'signfile.py' and 'signfolder.py' scripts in the 'scripts' folder.
    """

    # Considered SHA256 at first, but this is reportedly robust against something called 'length extension attacks'.
    __hash_algorithm = hashes.SHA384()

    # For (in) directories (plugins for example):
    __signatures_relative_filename = "signature.json"
    __root_signatures_category = "root_signatures"

    # For(/next to) single files:
    __signature_filename_extension = ".signature"
    __root_signature_entry = "root_signature"

    @staticmethod
    def defaultViolationHandler(message: str) -> None:
        """This violationHandler is called after any other handlers"""

        Logger.logException("e", message)
        raise TrustException()

    @classmethod
    def getHashAlgorithm(cls):
        """To ensure the same hash-algorithm is used by every part of this code.

        :return: The hash-algorithm used for the entire 'suite'.
        """

        return cls.__hash_algorithm

    @classmethod
    def getSignaturesLocalFilename(cls) -> str:
        """'Signed folder' scenario: Get the filename the signature file in a folder has.

        :return: The filename of the signatures file (not the path).
        """

        return cls.__signatures_relative_filename

    @classmethod
    def getRootSignatureCategory(cls) -> str:
        """'Signed folder' scenario: In anticipation of other keys, put the 'master' signature into this category.

        :return: The json 'name' for the main signatures category.
        """

        return cls.__root_signatures_category

    @classmethod
    def getSignaturePathForFile(cls, filename: str) -> str:
        """'Single signed file' scenario: Get the name of the signature-file that should be located next to the file.

        :param filename: The file that has (or needs to be) signed.
        :return: The path of the signature-file of this file.
        """

        return os.path.join(
            os.path.dirname(filename),
            os.path.basename(filename).split(".")[0] + cls.__signature_filename_extension
        )

    @classmethod
    def getRootSignatureEntry(cls) -> str:
        """'Single signed file' scenario: In anticipation of other keys, put the 'master' signature into this entry.

        :return: The json 'name' for the main signature.
        """

        return cls.__root_signature_entry

    @classmethod
    def getFilePathInfo(cls, base_folder_path: str, current_full_path: str, local_filename: str) -> Tuple[str, str]:
        """'Signed folder' scenario: When walking over directory, it's convenient to have the full path on one hand,
        and the 'name' of the file in the signature json file just below the signed directory on the other.

        :param base_folder_path: The signed folder(name), where the signature file resides.
        :param current_full_path: The full path to the current folder.
        :param local_filename: The local filename of the current file.
        :return: A tuple with the full path to the file on disk and the 'signed-folder-local' path of that same file.
        """

        name_on_disk = os.path.join(current_full_path, local_filename)
        name_in_data = name_on_disk.replace(base_folder_path, "").replace("\\", "/")
        return name_on_disk, name_in_data if not name_in_data.startswith("/") else name_in_data[1:]

    @classmethod
    def getFileHash(cls, filename: str) -> Optional[str]:
        """Gets the hash for the provided file.

        :param filename: The filename of the file to be hashed.
        :return: The hash of the file.
        """

        hasher = hashes.Hash(cls.__hash_algorithm, backend = default_backend())
        try:
            with open(filename, "rb") as file:
                hasher.update(file.read())
                return base64.b64encode(hasher.finalize()).decode("utf-8")
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't read '{0}' for plain hash generation.".format(filename))
        return None

    @classmethod
    def getFileSignature(cls, filename: str, private_key: RSAPrivateKey) -> Optional[str]:
        """Creates the signature for the (hash of the) provided file, given a private key.

        :param filename: The file to be signed.
        :param private_key: The private key used for signing.
        :return: The signature if successful, 'None' otherwise.
        """

        file_hash = cls.getFileHash(filename)
        if file_hash is None:
            return None
        try:
            file_hash_bytes = base64.b64decode(file_hash)
            signature_bytes = private_key.sign(
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(cls.__hash_algorithm), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(cls.__hash_algorithm)
            )
            return base64.b64encode(signature_bytes).decode("utf-8")
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't sign '{0}', no signature generated.".format(filename))
        return None

    @staticmethod
    def generateNewKeyPair() -> Tuple[RSAPrivateKeyWithSerialization, RSAPublicKey]:
        """Create a new private-public key-pair.

        :return: A tulple of private-key/public key.
        """

        private_key = rsa.generate_private_key(public_exponent = 65537, key_size = 4096, backend = default_backend())
        return private_key, private_key.public_key()

    @staticmethod
    def loadPrivateKey(private_filename: str, optional_password: Optional[str]) -> Optional[RSAPrivateKey]:
        """Load a private key from a file.

        :param private_filename: The filename of the file containing the private key.
        :param optional_password: The key can be signed with a password as well (or not).
        :return: The private key contained in the file.
        """

        try:
            password_bytes = None if optional_password is None else optional_password.encode()
            with open(private_filename, "rb") as file:
                private_key = load_pem_private_key(file.read(), backend=default_backend(), password=password_bytes)
                return private_key
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't load private-key.")
        return None

    @staticmethod
    def saveKeyPair(private_key: "RSAPrivateKeyWithSerialization", private_path: str, public_path: str, optional_password: Optional[str] = None) -> bool:
        """Save a key-pair to two distinct files.

        :param private_key: The private key to save. The public one will be generated from it.
        :param private_path: Path to the filename where the private key will be saved.
        :param public_path: Path to the filename where the public key will be saved.
        :param optional_password: The private key can be signed with a password as well (or not).
        :return: True on success.
        """

        try:
            encrypt_method = serialization.NoEncryption()  # type: ignore
            if optional_password is not None:
                encrypt_method = serialization.BestAvailableEncryption(optional_password.encode())  # type: ignore
            private_pem = private_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PrivateFormat.PKCS8,
                encryption_algorithm = encrypt_method
            )
            with open(private_path, "wb") as private_file:
                private_file.write(private_pem)

            public_pem = private_key.public_key().public_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PublicFormat.PKCS1
            )
            with open(public_path, "wb") as public_file:
                public_file.write(public_pem)

            Logger.log("i", "Private/public key-pair saved to '{0}','{1}'.".format(private_path, public_path))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Save private/public key to '{0}','{1}' failed.".format(private_path, public_path))
        return False

    @staticmethod
    def removeCached(path: str) -> bool:
        try:
            cache_folders_to_empty = []  # List[str]
            for root, dirnames, filenames in os.walk(path, followlinks=True):
                for dirname in dirnames:
                    if dirname == "__pycache__":
                        cache_folders_to_empty.append(os.path.join(root, dirname))
            for cache_folder in cache_folders_to_empty:
                for root, dirnames, filenames in os.walk(cache_folder, followlinks=True):
                    for filename in filenames:
                        os.remove(os.path.join(root, filename))
            return True
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Removal of pycache for unbundled path '{0}' failed.".format(path))
        return False


class Trust:
    """Trust for use in the main-application code, as opposed to the (keygen/signing) scripts.

    Can be seen as an elaborate wrapper around a public-key.
    Currently used as a singleton, as we currently have only one single 'master' public key for the entire app.
    See the 'createkeypair.py', 'signfile.py' and 'signfolder.py' scripts in the 'scripts' folder.
    """

    __instance = None

    @staticmethod
    def getPublicRootKeyPath() -> str:
        """It is assumed that the application will have a 'master' public key.

        :return: Path to the 'master' public key of this application.
        """

        return Resources.getPath(Resources.Resources, "public_key.pem")

    @classmethod
    def getInstance(cls):
        """Get the 'canonical' Trusts object for this application. See also 'getPublicRootKeyPath'.

        :raise Exception: if the public key in `getPublicRootKeyPath()` can't be loaded for some reason.
        :return: The Trust singleton.
        """

        if cls.__instance is None:
            cls.__instance = Trust(Trust.getPublicRootKeyPath())
        return cls.__instance

    @classmethod
    def getInstanceOrNone(cls):
        """Get the  'canonical' Trust object or None if not initialized yet

        Useful if only _optional_ verification is needed.

        :return: Trust singleton or None if problems occurred with loading the public key in `getPublicRootKeyPath()`.
        """

        try:
            return cls.getInstance()
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            return None

    def __init__(self, public_key_filename: str, pre_err_handler: Callable[[str], None] = None) -> None:
        """Initializes a Trust object. A Trust object represents a public key and related utility methods on that key.
        If the application only has a single public key, it's best to use 'getInstance' or 'getInstanceOrNone'.

        :param public_key_filename: Path to the file that holds the public key.
        :param pre_err_handler: An extra error handler which will be called before TrustBasics.defaultViolationHandler
                                Receives a human readable error string as argument.
        :raise Exception: if public key file provided by the argument can't be found or parsed.
        """

        self._public_key = None  # type: Optional[RSAPublicKey]
        try:
            with open(public_key_filename, "rb") as file:
                self._public_key = load_pem_public_key(file.read(), backend = default_backend())
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            self._public_key = None
            raise Exception("e", "Couldn't load public-key '{0}'.".format(public_key_filename))
            # NOTE: Handle _potential_ security violation outside of this initializer, in case it's just for validation.

        def violation_handler(message: str):
            if pre_err_handler is not None:
                pre_err_handler(message)
            TrustBasics.defaultViolationHandler(message=message)

        self._violation_handler = violation_handler  # type: Callable[[str], None]

    def _verifyFile(self, filename: str, signature: str) -> bool:
        if self._public_key is None:
            return False
        file_hash = TrustBasics.getFileHash(filename)
        if file_hash is None:
            return False
        try:
            signature_bytes = base64.b64decode(signature)
            file_hash_bytes = base64.b64decode(file_hash)
            self._public_key.verify(
                signature_bytes,
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(TrustBasics.getHashAlgorithm()), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(TrustBasics.getHashAlgorithm())
            )
            return True
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            self._violation_handler("Couldn't verify '{0}' with supplied signature.".format(filename))
        return False

    def signedFolderCheck(self, path: str) -> bool:
        """In the 'singed folder' case, check whether the folder is signed according to the Trust-objects' public key.

        :param path: The path to the folder to be checked (not the signature-file).
        :return: True if the folder is signed (contains a signatures-file) and signed correctly.
        """

        try:
            json_filename = os.path.join(path, TrustBasics.getSignaturesLocalFilename())

            # Open the file containing signatures:
            with open(json_filename, "r", encoding = "utf-8") as data_file:
                json_data = json.load(data_file)
                signatures_json = json_data.get(TrustBasics.getRootSignatureCategory(), None)
                if signatures_json is None:
                    Logger.logException("e", "Can't parse (folder) signature file '{0}'.".format(data_file))
                    return False

                # Loop over all files within the folder (excluding the signature file):
                file_count = 0
                for root, dirnames, filenames in os.walk(path, followlinks = True):
                    for filename in filenames:
                        if filename == TrustBasics.getSignaturesLocalFilename() and root == path:
                            continue
                        file_count += 1
                        name_on_disk, name_in_data = TrustBasics.getFilePathInfo(path, root, filename)

                        # Get the signature for the current to-verify file:
                        signature = signatures_json.get(name_in_data, None)
                        if signature is None:
                            self._violation_handler("File '{0}' was not signed with a checksum.".format(name_on_disk))
                            return False

                        # Verify the file:
                        if not self._verifyFile(name_on_disk, signature):
                            self._violation_handler("File '{0}' didn't match with checksum.".format(name_on_disk))
                            return False

                # The number of correctly signed files should be the same as the number of signatures:
                if len(signatures_json.keys()) != file_count:
                    self._violation_handler("Mismatch: # entries in '{0}' vs. real files.".format(json_filename))
                    return False

            Logger.log("i", "Verified unbundled folder '{0}'.".format(path))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            self._violation_handler("Can't find or parse signatures for unbundled folder '{0}'.".format(path))
        return False

    def signedFileCheck(self, filename: str) -> bool:
        """In the 'single signed file' case, check whether a file is signed according to the Trust-objects' public key.

        :param filename: The path to the file to be checked (not the signature-file).
        :return: True if the file is signed (is next to a signature file) and signed correctly.
        """

        try:
            signature_filename = TrustBasics.getSignaturePathForFile(filename)

            with open(signature_filename, "r", encoding = "utf-8") as data_file:
                json_data = json.load(data_file)
                signature = json_data.get(TrustBasics.getRootSignatureEntry(), None)
                if signature is None:
                    self._violation_handler("Can't parse signature file '{0}'.".format(signature_filename))
                    return False

                if not self._verifyFile(filename, signature):
                    self._violation_handler("File '{0}' didn't match with checksum.".format(filename))
                    return False

            Logger.log("i", "Verified unbundled file '{0}'.".format(filename))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            self._violation_handler("Can't find or parse signatures for unbundled file '{0}'.".format(filename))
        return False

    @staticmethod
    def signatureFileExistsFor(filename: str) -> bool:
        """Whether or not a signature file _exist_ (so _not_ necessarily correct)  for the provided (single file) path.

        :param filename: The filename that should be checked for.
        :return: Returns True if there is a signature file next to the provided single file (as opposed to folder).
        """

        return os.path.exists(TrustBasics.getSignaturePathForFile(filename))


class TrustException(Exception):
    pass
