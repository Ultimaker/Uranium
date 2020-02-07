# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import base64
import json
import os
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey, RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

from UM.Logger import Logger


# Anything shared between the main code and the (keygen/signing) scripts, does not need state:
class TrustBasics:
    __hash_algorithm = hashes.SHA384()

    # For directories (plugins for example):
    __signatures_relative_filename = "signature.json"
    __root_signatures_category = "root_signatures"

    # For(/next to) single files:
    __signature_filename_extension = ".signature"
    __root_signature_entry = "root_signature"

    @classmethod
    def getHashAlgorithm(cls):
        return cls.__hash_algorithm

    # Only used for in folders, there's another mechanism for 'loose' files:
    @classmethod
    def getSignaturesLocalFilename(cls) -> str:
        return cls.__signatures_relative_filename

    # Only used for in folders, there's another mechanism for 'loose' files:
    @classmethod
    def getRootSignatureCategory(cls) -> str:
        return cls.__root_signatures_category

    # Only used for single files, there's another mechanism for folders:
    @classmethod
    def getSignaturePathForFile(cls, filename: str) -> str:
        return os.path.join(
            os.path.dirname(filename),
            os.path.basename(filename).split(".")[0] + cls.__signature_filename_extension
        )

    # Only used for single files, there's another mechanism for folders:
    @classmethod
    def getRootSignatureEntry(cls) -> str:
        return cls.__root_signature_entry

    @classmethod
    def getFilePathInfo(cls, base_folder_path: str, current_full_path: str, local_filename: str) -> Tuple[str, str]:
        name_on_disk = os.path.join(current_full_path, local_filename)
        name_in_data = name_on_disk.replace(base_folder_path, "").replace("\\", "/")
        return name_on_disk, name_in_data if not name_in_data.startswith("/") else name_in_data[1:]

    @classmethod
    def getFileHash(cls, filename: str) -> Optional[str]:
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
        private_key = rsa.generate_private_key(public_exponent = 65537, key_size = 4096, backend = default_backend())
        return private_key, private_key.public_key()

    @staticmethod
    def loadPrivateKey(private_filename: str, optional_password: Optional[str]) -> Optional[RSAPrivateKey]:
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


# Trust as a singleton class for the main code, as opposed to the (keygen/signing) scripts:
class Trust:
    __instance = None

    @staticmethod
    def getPublicRootKeyPath() -> str:
        from UM.Application import Application
        return os.path.abspath(os.path.join(Application.getAppFolderPrefix(), "public_key.pem"))

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = Trust(Trust.getPublicRootKeyPath())
        return cls.__instance

    @classmethod
    def getInstanceOrNone(cls):
        try:
            return cls.getInstance()
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            return None

    def __init__(self, public_key_filename: str) -> None:
        self._public_key = None  #type: Optional[RSAPublicKey]
        try:
            with open(public_key_filename, "rb") as file:
                self._public_key = load_pem_public_key(file.read(), backend = default_backend())
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            self._public_key = None
            raise Exception("e", "Couldn't load public-key '{0}'.".format(public_key_filename))

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
            Logger.logException("e", "Couldn't verify '{0}' with supplied signature.".format(filename))
        return False

    def signedFolderCheck(self, path: str) -> bool:
        try:
            json_filename = os.path.join(path, TrustBasics.getSignaturesLocalFilename())

            with open(json_filename, "r", encoding = "utf-8") as data_file:
                json_data = json.load(data_file)
                signatures_json = json_data.get(TrustBasics.getRootSignatureCategory(), None)
                if signatures_json is None:
                    Logger.logException("e", "Can't parse (folder) signature file '{0}'.".format(data_file))
                    return False

                file_count = 0
                for root, dirnames, filenames in os.walk(path, followlinks = True):
                    for filename in filenames:
                        if filename == TrustBasics.getSignaturesLocalFilename() and root == path:
                            continue
                        file_count += 1
                        name_on_disk, name_in_data = TrustBasics.getFilePathInfo(path, root, filename)

                        signature = signatures_json.get(name_in_data, None)
                        if signature is None:
                            Logger.logException("e", "File '{0}' was not signed with a checksum.".format(name_on_disk))
                            return False

                        if not self._verifyFile(name_on_disk, signature):
                            Logger.logException("e", "File '{0}' didn't match with checksum.".format(name_on_disk))
                            return False

                if len(signatures_json.keys()) != file_count:
                    Logger.logException("e", "Mismatch: # entries in '{0}' vs. real files.".format(json_filename))
                    return False

            Logger.log("i", "Verified unbundled folder '{0}'.".format(path))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Can't find or parse signatures for unbundled folder '{0}'.".format(path))
        return False

    def signedFileCheck(self, filename: str) -> bool:
        try:
            signature_filename = TrustBasics.getSignaturePathForFile(filename)

            with open(signature_filename, "r", encoding = "utf-8") as data_file:
                json_data = json.load(data_file)
                signature = json_data.get(TrustBasics.getRootSignatureEntry(), None)
                if signature is None:
                    Logger.logException("e", "Can't parse signature file '{0}'.".format(signature_filename))
                    return False

                if not self._verifyFile(filename, signature):
                    Logger.logException("e", "File '{0}' didn't match with checksum.".format(filename))
                    return False

            Logger.log("i", "Verified unbundled file '{0}'.".format(filename))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Can't find or parse signatures for unbundled file '{0}'.".format(filename))
        return False

    @staticmethod
    def signatureFileExistsFor(filename: str) -> bool:
        return os.path.exists(TrustBasics.getSignaturePathForFile(filename))
