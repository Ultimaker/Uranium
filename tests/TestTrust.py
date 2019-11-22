import copy
from unittest.mock import patch, MagicMock
import pytest
import os
import random
import tempfile

from UM.Trust import TrustBasics, Trust

from scripts.signfile import signFile
from scripts.signfolder import signFolder

_folder_names = ["a", "b"]
_subfolder_names = ["sub", "."]
_file_names = ["x.txt", "y.txt", "z.txt"]
_passphrase = "swordfish"  # For code coverage: Securely storing a private key without one is probably better.

class TestTrust:

    # NOTE: Exhaustively testing trust is going to be difficult. We rely on audits (as well) in this matter.

    @pytest.fixture()
    def init_trust(self):
        # create a temporary directory and save a test key-pair to it:
        temp_dir = tempfile.TemporaryDirectory()
        temp_path = temp_dir.name
        private_key, public_key = TrustBasics.generateNewKeyPair()
        private_path = os.path.join(temp_path, "test_private_key.pem")
        public_path = os.path.join(temp_path, "test_public_key.pem")
        TrustBasics.saveKeyPair(private_key, private_path, public_path, _passphrase)

        # create random files:
        all_paths = [os.path.abspath(os.path.join(temp_path, x, y, z))
                     for x in _folder_names for y in _subfolder_names for z in _file_names]
        for path in all_paths:
            folder_path = os.path.dirname(path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(path, "w") as file:
                file.write("".join(random.choice(['a', 'b', 'c', '0', '1', '2', '\n']) for _ in range(1024)))

        # instantiate a trust object with the public key that was just generated:
        trust = Trust(public_path)  # Don't use Trust.getInstance as that uses the 'normal' public key instead of test.
        yield temp_path, private_path, trust

        temp_dir.cleanup()

    def test_signFileAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance = init_trust
        filepath_signed = os.path.join(temp_dir, _folder_names[0], _subfolder_names[0], _file_names[0])
        filepath_unsigned = os.path.join(temp_dir, _folder_names[1], _subfolder_names[0], _file_names[2])

        assert signFile(private_path, filepath_signed, _passphrase)

        assert trust_instance.signedFileCheck(filepath_signed)
        assert not trust_instance.signedFileCheck(filepath_unsigned)
        assert not trust_instance.signedFileCheck("file-not-found-check")

        public_key = copy.copy(trust_instance._public_key)
        trust_instance._public_key = None
        assert not trust_instance.signedFileCheck(filepath_signed)
        trust_instance._public_key = public_key

        with open(filepath_signed, "w") as file:
            file.write("\nPay 10 Golden Talents To Get Your Data Back Or Else\n")
        assert not trust_instance.signedFolderCheck(filepath_signed)

        os.remove(filepath_signed)
        assert not trust_instance.signedFolderCheck(filepath_signed)

    def test_signFolderAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance = init_trust
        folderpath_signed = os.path.join(temp_dir, _folder_names[0])
        folderpath_unsigned = os.path.join(temp_dir, _folder_names[1])

        assert signFolder(private_path, folderpath_signed, [], _passphrase)

        assert trust_instance.signedFolderCheck(folderpath_signed)
        assert not trust_instance.signedFolderCheck(folderpath_unsigned)
        assert not trust_instance.signedFileCheck("folder-not-found-check")

        public_key = copy.copy(trust_instance._public_key)
        trust_instance._public_key = None
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        trust_instance._public_key = public_key

        filepath = os.path.join(folderpath_signed, _subfolder_names[0], _file_names[1])
        with open(filepath, "w") as file:
            file.write("\nAlice and Bob will never notice this! Hehehehe.\n")
        assert not trust_instance.signedFolderCheck(folderpath_signed)

        os.remove(filepath)
        assert not trust_instance.signedFolderCheck(folderpath_signed)

    def test_initTrustFail(self):
        with pytest.raises(Exception):
            Trust("key-not-found")

        with pytest.raises(Exception):
            Trust.getInstance()

        assert Trust.getInstanceOrNone() is None

    def test_keyIOFails(self):
        private_key, public_key = TrustBasics.generateNewKeyPair()
        assert not TrustBasics.saveKeyPair(private_key, public_key, "file-not-found", _passphrase)
        assert TrustBasics.loadPrivateKey("key-not-found", _passphrase) is None

    def test_signNonexisting(self):
        private_key, public_key = TrustBasics.generateNewKeyPair()
        assert TrustBasics.getFileSignature("file-not-found", private_key) is None
