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

class TestTrust:

    # NOTE: Not exhaustive yet!

    @pytest.fixture()
    def init_trust(self):
        # create a temporary directory and save a test key-pair to it:
        temp_dir = tempfile.TemporaryDirectory()
        temp_path = temp_dir.name
        private_key, public_key = TrustBasics.generateNewKeyPair()
        private_path = os.path.join(temp_path, "test_private_key.pem")
        public_path = os.path.join(temp_path, "test_public_key.pem")
        TrustBasics.saveKeyPair(private_key, private_path, public_path)

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

        assert signFile(private_path, filepath_signed, None)

        assert trust_instance.signedFileCheck(filepath_signed)
        assert not trust_instance.signedFileCheck(filepath_unsigned)
        assert not trust_instance.signedFileCheck("file-not-found-check")

    def test_signFolderAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance = init_trust
        folderpath_signed = os.path.join(temp_dir, _folder_names[0])
        folderpath_unsigned = os.path.join(temp_dir, _folder_names[1])

        assert signFolder(private_path, folderpath_signed, [], None)

        assert trust_instance.signedFolderCheck(folderpath_signed)
        assert not trust_instance.signedFolderCheck(folderpath_unsigned)
        assert not trust_instance.signedFileCheck("folder-not-found-check")
