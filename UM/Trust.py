# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
import base64

from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from UM.Logger import Logger


class Trust:

    # TODO: Shift from classmethods to live object (so a Trust object may have a different pubkey/sigs-filename)

    _hash_algorithm = hashes.SHA3_384()
    _public_key = None  # type: Optional[RSAPublicKey]
    _public_key_filename = "public_key.pem"
    _signatures_relative_filename = "signature.json"

    # Methods for file/signature verifcation:

    @classmethod
    def _loadPublicKey(cls) -> Optional[RSAPublicKey]:
        try:
            with open(cls._public_key_filename, "rb") as file:
                return load_pem_public_key(file.read(), default_backend())
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't load public-key.")
        return None

    @classmethod
    def _getFileHash(cls, filename: str) -> str:
        hasher = hashes.Hash(cls._hash_algorithm, default_backend())
        try:
            with open(filename, "rb") as file:
                hasher.update(file.read())
                return base64.b64encode(hasher.finalize())
        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Couldn't read '{0}' for plain hash generation.".format(filename))
        return ""

    @classmethod
    def _verifyFile(cls, filename: str, signature: str) -> bool:
        if cls._public_key is None:
            cls._public_key = cls._loadPublicKey()
            if cls._public_key is None:
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
                padding.PSS(mgf=padding.MGF1(cls._hash_algorithm), salt_length=padding.PSS.MAX_LENGTH),
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

    @classmethod
    def _signFile(cls, filename: str, private_key: RSAPrivateKey) -> str:
        file_hash = cls._getFileHash(filename)
        if file_hash == "":
            return ""
        try:
            file_hash_bytes = base64.b64decode(file_hash)
            signature_bytes = private_key.sign(
                file_hash_bytes,
                padding.PSS(mgf = padding.MGF1(cls._hash_algorithm), salt_length = padding.PSS.MAX_LENGTH),
                Prehashed(cls._hash_algorithm)
            )
            return base64.b64encode(signature_bytes)
        except:
            Logger.logException("e", "Couldn't sign '{0}', no signature generated.".format(filename))
        return ""

    # Public methods (not to be confused with public keys):

    @classmethod
    def signedFolderCheck(cls, path: str) -> bool:
        try:
            json_filename = os.path.join(path, cls._signatures_relative_filename)

            with open(json_filename, "r", encoding="utf-8") as data_file:
                signatures_json = json.load(data_file)

                file_count = 0
                for root, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        if filename == cls._signatures_relative_filename:
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

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Can't find or parse signatures for unbundled folder '{0}'.".format(path))
            return False

        return True

    # TEMPORARY METHODS  / REMOVE:

    @classmethod
    def _smoketest(cls) -> None:
        test_filename = "C:/tmp/testsign.txt"

        private_key = cls._generateNewKeys()
        signature = cls._signFile(test_filename, private_key)
        trusted = cls._verifyFile(test_filename, signature)

        print("SIGNTURE: {0} #### {1}".format(signature, trusted))
