# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
import base64
from typing import List

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key

from UM.Logger import Logger


class Trust:

    # TODO: Shift from classmethods to live object (so a Trust object may have a different pubkey/sigs-filename)

    _hash_algorithm = hashes.SHA3_384()
    _public_key = None  # type: Optional[RSAPublicKey]
    _public_key_filename = "public_key.pem"  # TODO -> relative location of public key file w.r.t. application
    _signatures_relative_filename = "signature.json"

    # Methods for file/signature verifcation:

    @classmethod
    def _loadPublicKey(cls) -> bool:
        try:
            with open(cls._public_key_filename, "rb") as file:
                cls._public_key = load_pem_public_key(file.read(), backend = default_backend())
            return True
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't load public-key.")
        return False

    @classmethod
    def _getFileHash(cls, filename: str) -> str:
        hasher = hashes.Hash(cls._hash_algorithm, backend = default_backend())
        try:
            with open(filename, "rb") as file:
                hasher.update(file.read())
                return base64.b64encode(hasher.finalize()).decode("utf-8")
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't read '{0}' for plain hash generation.".format(filename))
        return ""

    @classmethod
    def _verifyFile(cls, filename: str, signature: str) -> bool:
        if cls._public_key is None:
            if not cls._loadPublicKey():
                return False
        file_hash = cls._getFileHash(filename)
        if file_hash == "":
            return False
        try:
            signature_bytes = base64.b64decode(signature)
            file_hash_bytes = base64.b64decode(file_hash)
            cls._public_key.verify(
                signature_bytes,
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(cls._hash_algorithm), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(cls._hash_algorithm)
            )
            return True
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't verify '{0}' with supplied signature.".format(filename))
        return False

    # Methods for generation of & signing with keys (for inclusion in scripts, testing, and/or reference):
    # NOTE: Private keys should not be present or have to be generated during any normal run!

    # returns private key, stores public key in this Trust object
    @classmethod
    def _generateNewKeys(cls) -> RSAPrivateKey:
        private_key = rsa.generate_private_key(public_exponent = 65537, key_size = 4096, backend = default_backend())
        cls._public_key = private_key.public_key()
        return private_key

    # returns private key, stores public key in this Trust object
    @classmethod
    def _saveKeys(cls, private_key: RSAPrivateKey, private_filename: str) -> bool:
        try:
            private_pem = private_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PrivateFormat.PKCS8,
                encryption_algorithm = serialization.NoEncryption()
            )
            with open(private_filename, "wb") as private_file:
                private_file.write(private_pem)

            public_pem = cls._public_key.public_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PublicFormat.PKCS1
            )
            with open(cls._public_key_filename, "wb") as public_file:
                public_file.write(public_pem)

            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Saving private-public key-tuple (to '{0}' and '{1}' respectively) failed.".format(private_filename, cls._public_key_filename))
        return False

    @classmethod
    def _loadPrivateKey(cls, private_filename: str) -> RSAPrivateKey:
        try:
            with open(private_filename, "rb") as file:
                return load_pem_private_key(file.read(), backend = default_backend(), password = None)
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't load private-key.")
        return None

    @classmethod
    def _signFile(cls, filename: str, private_key: RSAPrivateKey) -> str:
        file_hash = cls._getFileHash(filename)
        if file_hash == "":
            return False
        try:
            file_hash_bytes = base64.b64decode(file_hash)
            signature_bytes = private_key.sign(
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(cls._hash_algorithm), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(cls._hash_algorithm)
            )
            return base64.b64encode(signature_bytes).decode("utf-8")
        except:
            Logger.logException("e", "Couldn't sign '{0}', no signature generated.".format(filename))
        return ""

    # Public methods (not to be confused with public keys):

    @classmethod
    def signedFolderCheck(cls, path: str) -> bool:
        try:
            json_filename = os.path.join(path, cls._signatures_relative_filename)

            with open(json_filename, "r", encoding = "utf-8") as data_file:
                signatures_json = json.load(data_file)

                file_count = 0
                for root, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        if filename == cls._signatures_relative_filename and root == path:
                            continue
                        file_count += 1
                        name_on_disk = os.path.join(root, filename)
                        name_in_data = name_on_disk.replace(path, "").replace("\\", "/")

                        signature = signatures_json.get(name_in_data, None)
                        if signature is None:
                            Logger.logException("e", "File '{0}' was not signed with a checksum.".format(name_on_disk))
                            return False

                        if not cls._verifyFile(name_on_disk, signature):
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

    @classmethod
    def signFolder(cls, private_key: RSAPrivateKey, path: str, ignore_folders: List[str] = []) -> bool:
        try:
            signatures = {}  # Dict[str, str]

            for root, dirnames, filenames in os.walk(path):
                if os.path.basename(root) in ignore_folders:
                    continue
                for filename in filenames:
                    if filename == cls._signatures_relative_filename and root == path:
                        continue

                    name_on_disk = os.path.join(root, filename)
                    name_in_data = name_on_disk.replace(path, "").replace("\\", "/")
                    signatures[name_in_data] = cls._signFile(name_on_disk, private_key)

            json_filename = os.path.join(path, cls._signatures_relative_filename)
            with open(json_filename, "w", encoding = "utf-8") as data_file:
                json.dump(signatures, data_file, indent = 2)

            Logger.log("i", "Signed folder '{0}'.".format(path))
            return True

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't sign folder '{0}'.".format(path))
        return False

    # TEMPORARY METHODS  / move to or rebuild as unit-tests later:

    @classmethod
    def _smoketestA(cls) -> None:
        test_filename = "C:/tmp/testsign.txt"
        private_key_filename = "C:/tmp/private_key.pem"

        private_key = cls._generateNewKeys()
        signature = cls._signFile(test_filename, private_key)
        trusted = cls._verifyFile(test_filename, signature)

        print("SIGNTURE BEFORE: {0} #### {1}".format(signature, trusted))

        cls._saveKeys(private_key, private_key_filename)
        private_key = cls._loadPrivateKey(private_key_filename)
        cls._loadPublicKey()
        #private_key = cls._generateNewKeys()

        signature = cls._signFile(test_filename, private_key)
        #trusted = cls._verifyFile(test_filename, signature)

        print("SIGNTURE AFTER: {0} #### {1}".format(signature, trusted))

    @classmethod
    def _smoketestB(cls):
        private_key = cls._generateNewKeys()
        cls._saveKeys(private_key, "C:/tmp/private_key.pem")

        if cls.signFolder(private_key, "C:/tmp/SuperMirrorTool", ["__pycache__"]):
            print("****** SIGNED SUPERMIRRORTOOL ******")
        else:
            print("****** NOOOOOOOOOOOOOOOOOOOOO ******")

        if cls.signedFolderCheck("C:/tmp/SuperMirrorTool"):
            print("!!!!!! CHECKD SUPERMIRRORTOOL !!!!!!")
        else:
            print("!!!!!! NOOOOOOOOOOOOOOOOOOOOO !!!!!!")
