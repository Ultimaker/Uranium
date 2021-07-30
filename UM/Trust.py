# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import base64
import json
import os
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple, List, cast

# Note that we unfortunately need to use 'hazmat' code, as there apparently is no way to do what we want otherwise.
# (Even if what we want should be relatively commonplace in security.)
# Noted because if we _can_ make the change away from 'hazmat' (as opposed to lib-cryptography in general) we _should_.
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey, RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

from UM.CentralFileStorage import CentralFileStorage
from UM.Logger import Logger
from UM.Resources import Resources
from UM.Version import Version


class TrustBasics:
    """Anything shared between the main code and the (keygen/signing) scripts which does not need state.

    See 'Trust' (below) and the 'createkeypair.py', 'signfile.py' and 'signfolder.py' scripts in the 'scripts' folder.
    """

    # Considered SHA256 at first, but this is reportedly robust against something called 'length extension attacks'.
    __hash_algorithm = hashes.SHA384()

    # For (in) directories (plugins for example):
    __signatures_relative_filename = "signature.json"
    __central_storage_relative_filename = "central_storage.json"
    __root_signatures_category = "root_signatures"
    __root_signed_manifest_key = "root_manifest_signature"

    # For(/next to) single files:
    __signature_filename_extension = ".signature"
    __root_signature_entry = "root_signature"

    # Files that are cached should be removed before verifying:
    __cached_folder_names = ["__pycache__"]
    __cached_file_extentions = [".qmlc"]

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
    def getCentralStorageFilename(cls) -> str:
        return cls.__central_storage_relative_filename

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
    def getRootSignedManifestKey(cls) -> str:
        """'Signed folder' scenario: This is the (json-)key for the hash that (self-)signs the signing file.

        :return: The json 'name' for the key that contains the signature that signs all others' in the file.
        """

        return cls.__root_signed_manifest_key

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
    def getSelfSignHash(cls, signatures: Dict[str, str]) -> Optional[str]:
        """ Make a hash for the signature 'file' itself, where the file is represented as a dictionary here.

        :param signatures: A dictionary of (filename, file-hash-signature) pairs.
        :return: A hash, which can be used for creating or checking against a self-signed manifest.
        """

        concat = "".join([str(key) + str(signatures.get(key)) for key in sorted(signatures.keys())])
        if concat is None or len(concat) < 1:
            return None
        hasher = hashes.Hash(cls.__hash_algorithm, backend=default_backend())
        hasher.update(concat.encode())
        return base64.b64encode(hasher.finalize()).decode("utf-8")

    @classmethod
    def getHashSignature(cls, shash: str, private_key: RSAPrivateKey, err_info: Optional[str] = None) -> Optional[str]:
        """ Creates the signature for the provided hash, given a private key.

        :param shash: The provided string.
        :param private_key: The private key used for signing.
        :param err_info: Some optional extra info to be printed on error (for ex.: a filename the data came from).
        :return: The signature if successful, 'None' otherwise.
        """

        try:
            hash_bytes = base64.b64decode(shash)
            signature_bytes = private_key.sign(
                hash_bytes,
                padding.PSS(mgf=padding.MGF1(cls.__hash_algorithm), salt_length=padding.PSS.MAX_LENGTH),
                Prehashed(cls.__hash_algorithm)
            )
            return base64.b64encode(signature_bytes).decode("utf-8")
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            if err_info is None:
                err_info = "HASH:" + shash
            Logger.logException("e", "Couldn't sign '{0}', no signature generated.".format(err_info))
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
        return cls.getHashSignature(file_hash, private_key, filename)

    @staticmethod
    def generateNewKeyPair() -> Tuple[RSAPrivateKeyWithSerialization, RSAPublicKey]:
        """Create a new private-public key-pair.

        :return: A tuple of private-key/public key.
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
                return cast(RSAPrivateKey, private_key)
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

    @classmethod
    def removeCached(cls, path: str) -> bool:
        """ Removes any cached files and folders from a (folder) path (like __pycache__ and such).

        This not only prevents people from messing with these hardly checkable things, but also makes the code have less
        exceptions, since it can be assumed afterwards that the folder is in some sort of 'canonical' state.

        :param path: The path to remove any cached files or folders from.
        :return: Whether this operation succeeded.
        """
        try:
            cache_folders_to_empty = []  # type: List[str]
            cache_files_to_remove = []  # type: List[str]
            for root, dirnames, filenames in os.walk(path, followlinks=True):
                for dirname in dirnames:
                    if dirname in cls.__cached_folder_names:
                        cache_folders_to_empty.append(os.path.join(root, dirname))
                for filename in filenames:
                    if Path(filename).suffix in cls.__cached_file_extentions:
                        cache_files_to_remove.append(os.path.join(root, filename))
            for cache_folder in cache_folders_to_empty:
                for root, dirnames, filenames in os.walk(cache_folder, followlinks=True):
                    for filename in filenames:
                        os.remove(os.path.join(root, filename))
            for cache_file in cache_files_to_remove:
                os.remove(cache_file)
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Removal of pycache for unbundled path '{0}' failed.".format(path))
        return False

    @staticmethod
    def isPathInLocation(location: str, path: str) -> bool:
        """ Whether a path is a sub-folder (or equal) of a given location (path).

        :param location: The given path the other path should be a (sub-)folder of.
        :param path: The presumptive (sub-)folder.
        :return: True if path is equal to or matches but deeper than location, False otherwise.
        """
        try:
            canonical_location = os.path.normpath(location)
            canonical_path = os.path.normpath(path)
            is_in_path = os.path.commonpath([canonical_location, canonical_path]).startswith(canonical_location)
        except ValueError:
            is_in_path = False
        return is_in_path


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
        self._follow_symlinks = False  # type: bool

        try:
            with open(public_key_filename, "rb") as file:
                self._public_key = cast(RSAPublicKey, load_pem_public_key(file.read(), backend = default_backend()))
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            self._public_key = None
            raise Exception("e", "Couldn't load public-key '{0}'.".format(public_key_filename))
            # NOTE: Handle _potential_ security violation outside of this initializer, in case it's just for validation.

        def violation_handler(message: str):
            if pre_err_handler is not None:
                pre_err_handler(message)
            TrustBasics.defaultViolationHandler(message=message)

        self._violation_handler = violation_handler  # type: Callable[[str], None]

    def _verifyHash(self, shash: str, signature: str, err_info: Optional[str] = None) -> bool:
        if self._public_key is None:
            return False
        try:
            signature_bytes = base64.b64decode(signature)
            hash_bytes = base64.b64decode(shash)
            self._public_key.verify(
                signature_bytes,
                hash_bytes,
                padding.PSS(mgf = padding.MGF1(TrustBasics.getHashAlgorithm()), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(TrustBasics.getHashAlgorithm())
            )
            return True
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            if err_info is None:
                err_info = "HASH:" + shash
            self._violation_handler("Couldn't verify '{0}' with supplied signature.".format(err_info))
        return False

    def _verifyFile(self, filename: str, signature: str) -> bool:
        file_hash = TrustBasics.getFileHash(filename)
        if file_hash is None:
            return False
        return self._verifyHash(file_hash, signature, filename)

    def _verifyManifestIntegrety(self, signatures_json: Dict[str, str], json_data: Dict[str, str]) -> bool:
        try:
            self_sign = json_data.get(TrustBasics.getRootSignedManifestKey(), None)
            if self_sign is None:
                return False
            shash = TrustBasics.getSelfSignHash(signatures_json)
            if shash is None or not self._verifyHash(shash, self_sign):
                return False
            return True
        except:  # Yes, we do really want this on _every_ exception that might occur.
            return False

    def signedFolderPreStorageCheck(self, path: str) -> bool:
        """Do a quick check whether the 'central storage file' of a folder has been tampered with. This is necessary,
        since the central storage system (which otherwise runs first) copies files, and the copying of files itself
        can be an attack. Note that right after copying, a full check can be done, so the files themselves don't have
        to be checked yet (since that happens in the full check after copying).

        Shared pools of versioned items ('central storage') are used if a folder contains a 'central storage file'.
        (See the CentralFileStorage class for details.) The 'canonical' version of a folder as far as the Trust system
        is concerned, is the one where the items are already in central storage. Otherwise there would either be a whole
        range of 'acceptable answers' (and that's harder to test against) or, there would always be a need to verify
        a situation that shouldn't be that frequent (items need to be copied to central storage). This creates a problem
        in that the central storage mechanism needs to run _first_, however. The central storage has its own security
        measures, but this means that the central storage file in a folder (which contains info on what items should be
        copied) hasn't been checked against the trust manifest file in that folder yet.

        This only concerns the signature of the central storage file (and the correctness of the manifest file itself).
        Per separation of concern, and since the storage system already needs to be aware of security, any other
        'sanity checks' on the contents central storage file itself are the job of that system.

        :param path: The folder to do a quick pre-move check for.
        :return: True if the central-storage file is correctly signed. A folder without such a file is correct as well.
        """

        try:
            # Check if the central storage file exist, if not, then the system won't copy anything in any case.
            central_storage_filename = os.path.join(path, TrustBasics.getCentralStorageFilename())
            if not os.path.exists(central_storage_filename):
                Logger.log("i", f"No central storage file for unbundled folder '{path}'.")
                return True

            # Open the file containing signatures (just reading the json is negligible compared to the verify or store):
            manifest_path = os.path.join(path, TrustBasics.getSignaturesLocalFilename())
            with open(manifest_path, "r", encoding = "utf-8") as manifest_file:
                manifest_content = json.load(manifest_file)
                file_signatures = manifest_content.get(TrustBasics.getRootSignatureCategory(), None)
                if file_signatures is None:
                    self._violation_handler(f"Can't parse (folder) signature file '{manifest_file}' in '{path}'.")
                    return False

                # Check if there is an entry, since this file is known to exist in the folder:
                central_storage_basename = TrustBasics.getCentralStorageFilename()
                if central_storage_basename not in file_signatures:
                    self._violation_handler(f"Central storage file not signed for '{path}'.")
                    return False

                # Verify that the central storage file hasn't been tampered with:
                if not self._verifyFile(central_storage_filename, file_signatures[central_storage_basename]):
                    self._violation_handler(f"Central storage file does not match signature for '{path}'.")
                    return False

                # Check if the signing file itself has been tampered with (manifest is self-signed):
                if not self._verifyManifestIntegrety(file_signatures, manifest_content):
                    self._violation_handler(f"Manifest '{manifest_path}' is not properly self-signed in '{path}'.")
                    return False

            # Check if the central storage file doesn't contain files that would be moved outside the plugin folder, or
            # files that would be moved to outside of the central storage location:
            with open(central_storage_filename, "r", encoding = "utf-8") as central_storage_file:
                central_storage_list = json.loads(central_storage_file.read())

                storage_location = CentralFileStorage.getCentralStorageLocation()
                for file_to_move in central_storage_list:

                    # Any file is not from outside of the plugin:
                    source_full_path = os.path.join(path, file_to_move[0])
                    if not TrustBasics.isPathInLocation(path, source_full_path):
                        self._violation_handler(f"Item to store '{file_to_move[0]}' is from outside of '{path}'.")
                        return False

                    # Any file does not go outside of storage territory:
                    dest_full_path = os.path.join(storage_location, file_to_move[1])
                    if not TrustBasics.isPathInLocation(storage_location, dest_full_path):
                        self._violation_handler(f"Move '{file_to_move[0]}' from '{path}' to outside of storage folder.")
                        return False

            # Otherwise, as far as this quick pre check is concerned, there is nothing wrong:
            Logger.log("i", f"Central storage file signed correctly for '{path}'.")
            return True

        except:  # Yes, we do really want this on _every_ exception that might occur.
            self._violation_handler(f"Exception during verification of central storage file for '{path}'.")
        return False

    def signedFolderCheck(self, path: str) -> bool:
        """In the 'singed folder' case, check whether the folder is signed according to the Trust-objects' public key.

        :param path: The path to the folder to be checked (not the signature-file).
        :return: True if the folder is signed (contains a signatures-file) and signed correctly.
        """

        try:
            manifest_path = os.path.join(path, TrustBasics.getSignaturesLocalFilename())
            storage_filename = os.path.join(path, TrustBasics.getCentralStorageFilename())

            storage_list = None
            if os.path.exists(storage_filename):
                with open(storage_filename, "r", encoding = "utf-8") as storage_file:
                    storage_list = json.load(storage_file)

            # Open the file containing signatures:
            with open(manifest_path, "r", encoding = "utf-8") as manifest_file:
                manifest_content = json.load(manifest_file)
                file_signatures = manifest_content.get(TrustBasics.getRootSignatureCategory(), None)
                if file_signatures is None:
                    self._violation_handler("Can't parse (folder) signature file '{0}'.".format(manifest_file))
                    return False

                # Any filename outside of the plugin-root is a sure sign of tampering:
                for key in file_signatures.keys():
                    if ".." in key:
                        self._violation_handler("Suspect key '{0}' in signature file '{1}'.".format(key, manifest_file))
                        return False

                # Check if the signing file itself has been tampered with (manifest is self-signed):
                if not self._verifyManifestIntegrety(file_signatures, manifest_content):
                    self._violation_handler(f"Manifest '{manifest_file}' is not properly self-signed in '{path}'.")
                    return False

                # Loop over all files within the folder (excluding the signature file):
                file_count = 0
                for root, dirnames, filenames in os.walk(path, followlinks = self._follow_symlinks):
                    for filename in filenames:
                        if filename == TrustBasics.getSignaturesLocalFilename() and root == path:
                            continue
                        name_on_disk, name_in_data = TrustBasics.getFilePathInfo(path, root, filename)
                        file_count += 1

                        # Get the signature for the current to-verify file:
                        signature = file_signatures.get(name_in_data, None)
                        if signature is None:
                            self._violation_handler("File '{0}' was not signed with a checksum.".format(name_on_disk))
                            return False

                        # Verify the file:
                        if not self._verifyFile(name_on_disk, signature):
                            self._violation_handler("File '{0}' didn't match with checksum.".format(name_on_disk))
                            return False
                    for dirname in dirnames:
                        dir_full_path = os.path.join(path, dirname)
                        if os.path.islink(dir_full_path) and not self._follow_symlinks:
                            Logger.log("w", "Directory symbolic link '{0}' will not be followed.".format(dir_full_path))

                # Check if the files moved to storage are still correct.
                if storage_list:
                    for entry in storage_list:
                        try:
                            # If this doesn't raise an exception, it's correct, since central storage uses hashes.
                            central_storage_path = CentralFileStorage.retrieve(entry[1], entry[3], Version(entry[2]))

                            # File could have been removed during execution (also helps with tests).
                            if not os.path.exists(central_storage_path):
                                continue

                            # If a directory was moved, add all the files in that directory to the file_count. For
                            # individual files mentioned in the central_storage.json increment the file_count by 1.
                            if os.path.isdir(central_storage_path):
                                file_count += sum([len(files) for _, _, files in os.walk(central_storage_path)])
                            elif os.path.isfile(central_storage_path):
                                file_count += 1
                        except (EnvironmentError, IOError):
                            self._violation_handler(f"Couldn't verify at least one centrally stored file for '{path}'.")
                            return False

                # The number of correctly signed files should be the same as the number of signatures:
                if len(file_signatures.keys()) != file_count:
                    self._violation_handler("Mismatch: # entries in '{0}' vs. real files.".format(manifest_path))
                    return False

            Logger.log("i", "Verified unbundled folder '{0}'.".format(path))
            return True

        except:  # Yes, we do really want this on _every_ exception that might occur.
            self._violation_handler(f"Exception during verification of unbundled folder '{path}'.")
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

        except:  # Yes, we do really want this on _every_ exception that might occur.
            self._violation_handler(f"Exception during verification of unbundled file '{filename}'.")
        return False

    @staticmethod
    def signatureFileExistsFor(filename: str) -> bool:
        """Whether or not a signature file _exist_ (so _not_ necessarily correct)  for the provided (single file) path.

        :param filename: The filename that should be checked for.
        :return: Returns True if there is a signature file next to the provided single file (as opposed to folder).
        """

        return os.path.exists(TrustBasics.getSignaturePathForFile(filename))

    def setFollowSymlinks(self, follow_symlinks: bool) -> None:
        self._follow_symlinks = follow_symlinks


class TrustException(Exception):
    pass
