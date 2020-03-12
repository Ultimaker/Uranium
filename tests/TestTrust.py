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
        # Create a temporary directory and save a test key-pair to it:
        temp_dir = tempfile.TemporaryDirectory()
        temp_path = temp_dir.name
        private_key, public_key = TrustBasics.generateNewKeyPair()
        private_path = os.path.join(temp_path, "test_private_key.pem")
        public_path = os.path.join(temp_path, "test_public_key.pem")
        TrustBasics.saveKeyPair(private_key, private_path, public_path, _passphrase)

        # Create random files:
        all_paths = [os.path.abspath(os.path.join(temp_path, x, y, z))
                     for x in _folder_names for y in _subfolder_names for z in _file_names]
        for path in all_paths:
            folder_path = os.path.dirname(path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(path, "w") as file:
                file.write("".join(random.choice(['a', 'b', 'c', '0', '1', '2', '\n']) for _ in range(1024)))

        # Instantiate a trust object with the public key that was just generated:
        violation_callback = MagicMock()
        trust = Trust(public_path)  # No '.getInstance', since key & handler provided.
        trust._violation_handler = violation_callback
        yield temp_path, private_path, trust, violation_callback

        temp_dir.cleanup()

    def test_signFileAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance, violation_callback = init_trust
        filepath_signed = os.path.join(temp_dir, _folder_names[0], _subfolder_names[0], _file_names[0])
        filepath_unsigned = os.path.join(temp_dir, _folder_names[1], _subfolder_names[0], _file_names[2])

        # Attempt to sign a file.
        assert signFile(private_path, filepath_signed, _passphrase)

        # Check if we're able to verify the file we just signed.
        assert trust_instance.signedFileCheck(filepath_signed)
        assert violation_callback.call_count == 0  # No violation

        # Check if the file we didn't sign notifies us about this.
        assert not trust_instance.signedFileCheck(filepath_unsigned)
        assert violation_callback.call_count == 1

        # An unknown file is also seen as an invalid one.
        assert not trust_instance.signedFileCheck("file-not-found-check")
        assert violation_callback.call_count == 2

        # The signing should fail if we disable the key (since we can't confirm anything)
        public_key = copy.copy(trust_instance._public_key)
        trust_instance._public_key = None
        assert not trust_instance.signedFileCheck(filepath_signed)
        assert violation_callback.call_count == 3
        violation_callback.reset_mock()
        trust_instance._public_key = public_key

        # Oh noes! Someone changed the file!
        with open(filepath_signed, "w") as file:
            file.write("\nPay 10 Golden Talents To Get Your Data Back Or Else\n")
        assert not trust_instance.signedFolderCheck(filepath_signed)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

        # If one file is missing, the entire folder isn't considered to be signed.
        os.remove(filepath_signed)
        assert not trust_instance.signedFolderCheck(filepath_signed)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

    def test_signFolderAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance, violation_callback = init_trust
        folderpath_signed = os.path.join(temp_dir, _folder_names[0])
        folderpath_unsigned = os.path.join(temp_dir, _folder_names[1])

        # Attempt to sign a folder & validate it's signatures.
        assert signFolder(private_path, folderpath_signed, [], _passphrase)
        assert trust_instance.signedFolderCheck(folderpath_signed)

        # A folder that is not signed should be seen as such
        assert not trust_instance.signedFolderCheck(folderpath_unsigned)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

        # Unknown folders should also be seen as unsigned
        assert not trust_instance.signedFileCheck("folder-not-found-check")
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

        # After removing the key, the folder that was signed should be seen as unsigned.
        public_key = copy.copy(trust_instance._public_key)
        trust_instance._public_key = None
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()
        trust_instance._public_key = public_key

        # Any modification will should also invalidate it.
        filepath = os.path.join(folderpath_signed, _subfolder_names[0], _file_names[1])
        with open(filepath, "w") as file:
            file.write("\nAlice and Bob will never notice this! Hehehehe.\n")
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        assert violation_callback.call_count > 0
        violation_callback.reset_mock()

        os.remove(filepath)
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

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
