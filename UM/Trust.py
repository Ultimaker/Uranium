# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
import base64
from typing import List, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

from UM.Logger import Logger

class Trust:
    __instance = None

    @classmethod
    def getInstance(cls):
        from UM.Application import Application
        if not cls.__instance:
            cls.__instance = Trust(os.path.abspath(os.path.join(Application.getInstallPrefix(), "public_key.pem")))
        return cls.__instance

    def __init__(self, public_key_filename: str) -> bool:
        self._hash_algorithm = hashes.SHA3_384()
        self._signatures_relative_filename = "signature.json"  # <- For directories (plugins for example).
        self._signature_filename_extension = ".signature"      # <- For(/next to) single files.

        self._public_key_filename = public_key_filename
        self._public_key = None  #type: Optional[RSAPublicKey]

        if self._public_key_filename is not None:
            try:
                with open(self._public_key_filename, "rb") as file:
                    self._public_key = load_pem_public_key(file.read(), backend = default_backend())
            except:  # Yes, we  do really want this on _every_ exception that might occur.
                Logger.logException("e", "Couldn't load public-key.")
                self._public_key = None

    def _getFileHash(self, filename: str) -> str:
        hasher = hashes.Hash(self._hash_algorithm, backend = default_backend())
        try:
            with open(filename, "rb") as file:
                hasher.update(file.read())
                return base64.b64encode(hasher.finalize()).decode("utf-8")
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't read '{0}' for plain hash generation.".format(filename))
        return ""

    def _verifyFile(self, filename: str, signature: str) -> bool:
        if self._public_key is None:
            return False
        file_hash = self._getFileHash(filename)
        if file_hash == "":
            return False
        try:
            signature_bytes = base64.b64decode(signature)
            file_hash_bytes = base64.b64decode(file_hash)
            self._public_key.verify(
                signature_bytes,
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(self._hash_algorithm), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(self._hash_algorithm)
            )
            return True
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't verify '{0}' with supplied signature.".format(filename))
        return False

    # Methods for generation of & signing with keys (for inclusion in scripts, testing, and/or reference):
    # NOTE: Private keys should not be present or have to be generated during any normal run!

    # returns private key, stores public key in this Trust object
    def _generateNewKeys(self) -> RSAPrivateKey:
        private_key = rsa.generate_private_key(public_exponent = 65537, key_size = 4096, backend = default_backend())
        self._public_key = private_key.public_key()
        return private_key

    # returns private key, stores public key in this Trust object
    def _saveKeys(self, private_key: RSAPrivateKey, private_filename: str) -> bool:
        try:
            private_pem = private_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PrivateFormat.PKCS8,
                encryption_algorithm = serialization.NoEncryption()
            )
            with open(private_filename, "wb") as private_file:
                private_file.write(private_pem)

            public_pem = self._public_key.public_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PublicFormat.PKCS1
            )
            with open(self._public_key_filename, "wb") as public_file:
                public_file.write(public_pem)

            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Saving private-public key-tuple (to '{0}' and '{1}' respectively) failed.".format(private_filename, self._public_key_filename))
        return False

    def _loadPrivateKey(self, private_filename: str) -> RSAPrivateKey:
        try:
            with open(private_filename, "rb") as file:
                return load_pem_private_key(file.read(), backend = default_backend(), password = None)
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't load private-key.")
        return None

    def _signFile(self, filename: str, private_key: RSAPrivateKey) -> str:
        file_hash = self._getFileHash(filename)
        if file_hash == "":
            return ""
        try:
            file_hash_bytes = base64.b64decode(file_hash)
            signature_bytes = private_key.sign(
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(self._hash_algorithm), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(self._hash_algorithm)
            )
            return base64.b64encode(signature_bytes).decode("utf-8")
        except:
            Logger.logException("e", "Couldn't sign '{0}', no signature generated.".format(filename))
        return ""

    # Only used for single files, there's another mechanism for folders.
    def _getSignatureFilenameFor(self, filename: str):
        return os.path.join(
            os.path.dirname(filename),
            os.path.basename(filename).split(".")[0] + self._signature_filename_extension
        )

    # Public methods (not to be confused with public keys):

    def signedFolderCheck(self, path: str) -> bool:
        try:
            json_filename = os.path.join(path, self._signatures_relative_filename)

            with open(json_filename, "r", encoding = "utf-8") as data_file:
                signatures_json = json.load(data_file)

                file_count = 0
                for root, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        if filename == self._signatures_relative_filename and root == path:
                            continue
                        file_count += 1
                        name_on_disk = os.path.join(root, filename)
                        name_in_data = name_on_disk.replace(path, "").replace("\\", "/")

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
            signature_filename = self._getSignatureFilenameFor(filename)

            with open(signature_filename, "r", encoding = "utf-8") as data_file:
                signature = data_file.read()

                if signature is None:
                    Logger.logException("e", "Signature file '{0}' is not present.".format(signature_filename))
                    return False

                if not self._verifyFile(filename, signature):
                    Logger.logException("e", "File '{0}' didn't match with checksum.".format(filename))
                    return False

            Logger.log("i", "Verified unbundled file '{0}'.".format(filename))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Can't find or parse signatures for unbundled file '{0}'.".format(filename))
        return False

    def signatureFileExistsFor(self, filename: str) -> bool:
        return os.path.exists(self._getSignatureFilenameFor(filename))

    def signFolder(self, private_key: RSAPrivateKey, path: str, ignore_folders: List[str] = []) -> bool:
        try:
            signatures = {}  # Dict[str, str]

            for root, dirnames, filenames in os.walk(path):
                if os.path.basename(root) in ignore_folders:
                    continue
                for filename in filenames:
                    if filename == self._signatures_relative_filename and root == path:
                        continue

                    name_on_disk = os.path.join(root, filename)
                    name_in_data = name_on_disk.replace(path, "").replace("\\", "/")
                    signature = self._signFile(name_on_disk, private_key)
                    if signature == "":
                        Logger.logException("e", "Couldn't sign file '{0}'.".format(name_on_disk))
                        return False
                    signatures[name_in_data] = signature

            json_filename = os.path.join(path, self._signatures_relative_filename)
            with open(json_filename, "w", encoding = "utf-8") as data_file:
                json.dump(signatures, data_file, indent = 2)

            Logger.log("i", "Signed folder '{0}'.".format(path))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't sign folder '{0}'.".format(path))
        return False

    def signFile(self, private_key: RSAPrivateKey, filename: str) -> bool:
        try:
            signature = self._signFile(filename, private_key)
            if signature == "":
                Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
                return False

            signature_filename = self._getSignatureFilenameFor(filename)
            with open(signature_filename, "w", encoding = "utf-8") as data_file:
                data_file.write(signature)

            Logger.log("i", "Signed file '{0}'.".format(filename))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
        return False
