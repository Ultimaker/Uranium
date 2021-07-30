import copy
import json
from unittest.mock import MagicMock, patch
import os
import pytest
import random
import tempfile

from UM.CentralFileStorage import CentralFileStorage
from UM.Trust import TrustBasics, Trust

from scripts.signfile import signFile
from scripts.signfolder import signFolder

_folder_names = ["signed", "unsigned", "large"]
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

        # Set up mocked Central File Storage & plugin file (don't move the files yet, though):
        CentralFileStorage.setIsEnterprise(True)

        central_storage_dir = tempfile.TemporaryDirectory()
        central_storage_path = central_storage_dir.name
        large_plugin_path = os.path.join(temp_path, _folder_names[2])
        store_folder = os.path.join(large_plugin_path, _subfolder_names[0])
        store_file = os.path.join(large_plugin_path, _file_names[2])

        central_storage_dict = [
            [f"{_subfolder_names[0]}", f"{_subfolder_names[0]}", "1.0.0", CentralFileStorage._hashItem(store_folder)],
            [f"{_file_names[2]}", f"{_file_names[2]}", "1.0.0", CentralFileStorage._hashItem(store_file)]
        ]
        central_storage_file_path = os.path.join(large_plugin_path, TrustBasics.getCentralStorageFilename())
        with open(central_storage_file_path, "w") as file:
            json.dump(central_storage_dict, file, indent = 2)

        # Instantiate a trust object with the public key that was just generated:
        violation_callback = MagicMock()
        trust = Trust(public_path)  # No '.getInstance', since key & handler provided.
        trust._violation_handler = violation_callback
        yield temp_path, private_path, trust, violation_callback, central_storage_path

        temp_dir.cleanup()
        central_storage_dir.cleanup()
        CentralFileStorage.setIsEnterprise(False)

    def test_signFileAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance, violation_callback, _ = init_trust
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
        assert not trust_instance.signedFileCheck(filepath_signed)
        assert violation_callback.call_count > 0
        violation_callback.reset_mock()

    def test_signFolderAndPreStorageCheck(self, init_trust):
        temp_dir, private_path, trust_instance, violation_callback, central_storage_dir = init_trust
        folderpath_signed = os.path.join(temp_dir, _folder_names[2])
        folderpath_without_storage = os.path.join(temp_dir, _folder_names[0])
        # Note that we don't do anything with the storage here yet, after all, this is a _pre_-storage check.

        # Verify completely unsigned folder should fail:
        assert not trust_instance.signedFolderPreStorageCheck(folderpath_signed)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

        # Signing it, then verify, should succeed:
        assert signFolder(private_path, folderpath_signed, [], _passphrase)
        assert trust_instance.signedFolderPreStorageCheck(folderpath_signed)

        # A folder without a central storage file should just pass, no matter what:
        assert trust_instance.signedFolderPreStorageCheck(folderpath_without_storage)

        # From here on out, make sure we're testing the other part of that functionality (prevent early out):
        trust_instance._verifyFile = MagicMock(return_value = True)
        trust_instance._verifyManifestIntegrety = MagicMock(return_value=True)

        # Overwrite the central storage dictionary with files moved to an arbitrary location (then fail the check):
        central_storage_dict = [["/root/.importantfile", "/home/eve", "1.0.0", "dummy"]]
        central_storage_file_path = os.path.join(folderpath_signed, TrustBasics.getCentralStorageFilename())
        with open(central_storage_file_path, "w") as file:
            json.dump(central_storage_dict, file, indent=2)
        assert not trust_instance.signedFolderPreStorageCheck(folderpath_signed)

        # Overwrite the central storage dictionary with files-to-move outside of the storage area (then fail the check):
        central_storage_dict = [["signatures.json", "../../signatures.json", "1.0.0", "dummy"]]
        central_storage_file_path = os.path.join(folderpath_signed, TrustBasics.getCentralStorageFilename())
        with open(central_storage_file_path, "w") as file:
            json.dump(central_storage_dict, file, indent=2)
        assert not trust_instance.signedFolderPreStorageCheck(folderpath_signed)

    def test_signFolderAndVerify(self, init_trust):
        temp_dir, private_path, trust_instance, violation_callback, central_storage_dir = init_trust
        folderpath_signed = os.path.join(temp_dir, _folder_names[0])
        folderpath_unsigned = os.path.join(temp_dir, _folder_names[1])
        folderpath_large = os.path.join(temp_dir, _folder_names[2])

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

        # Hecking around with the signature file should also be discouraged.
        signatures_file = os.path.join(folderpath_signed, TrustBasics.getSignaturesLocalFilename())
        with open(signatures_file, "r", encoding = "utf-8") as sigfile:
            sig_json = json.load(sigfile)
        restore_json = copy.copy(sig_json)
        sig_json[TrustBasics.getRootSignedManifestKey()] = "HAHAHAHA"
        os.remove(signatures_file)
        with open(signatures_file, "w", encoding = "utf-8") as sigfile:
            json.dump(sig_json, sigfile, indent = 2)
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        assert violation_callback.call_count > 0
        violation_callback.reset_mock()
        os.remove(signatures_file)
        with open(signatures_file, "w", encoding = "utf-8") as sigfile:
            json.dump(restore_json, sigfile, indent = 2)

        # Any modification should also invalidate it.
        filepath = os.path.join(folderpath_signed, _subfolder_names[0], _file_names[1])
        with open(filepath, "w") as file:
            file.write("\nAlice and Bob will never notice this! Hehehehe.\n")
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        assert violation_callback.call_count > 0
        violation_callback.reset_mock()

        # Any missing files should also be registered.
        os.remove(filepath)
        assert not trust_instance.signedFolderCheck(folderpath_signed)
        assert violation_callback.call_count == 1
        violation_callback.reset_mock()

        # * 'Central file storage'-enabled section *
        with patch("UM.CentralFileStorage.CentralFileStorage.getCentralStorageLocation", MagicMock(return_value = central_storage_dir)):

            # Do some set-up (signing, moving files around with the central file storage):
            assert signFolder(private_path, folderpath_large, [], _passphrase)
            assert violation_callback.call_count == 0
            subfolder_path = os.path.join(folderpath_large, _subfolder_names[0])
            file_path = os.path.join(folderpath_large, _file_names[2])
            stored_file_path = os.path.join(central_storage_dir, _file_names[2] + ".1.0.0")
            CentralFileStorage.store(subfolder_path, _subfolder_names[0], "1.0.0", True)
            CentralFileStorage.store(file_path, _file_names[2], "1.0.0", True)

            # Should pass signed folder check, even though files have moved to central storage:
            assert trust_instance.signedFolderCheck(folderpath_large)
            assert violation_callback.call_count == 0

            # Should not pass the signed folder check if one of the files doesn't have the right hash in storage.
            with open(stored_file_path, "w") as file:
                file.write("\nWhoopsadoodle, the file just changed suddenly.\n")
            assert not trust_instance.signedFolderCheck(folderpath_large)
            assert violation_callback.call_count > 0
            violation_callback.reset_mock()

            # Should not pass the signed folder check if one of the files is missing, even in storage.
            os.remove(stored_file_path)
            assert not trust_instance.signedFolderCheck(folderpath_large)
            assert violation_callback.call_count > 0
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

    @pytest.mark.parametrize("location,subfolder", [
        (r"/a/b/c", r"/a/b/c/d"),
        (r"/a/b/c", r"/a/b/c/d/.."),
        (r"/a/b/c", r"/a/b/../b/c/d/../e"),
        (r"/a/b/../d/c", r"/a/d/c")
    ])
    def test_isPathInLocation(self, location, subfolder):
        assert TrustBasics.isPathInLocation(location, subfolder)

    @pytest.mark.parametrize("location,subfolder", [
        (r"/a/b/c", r"/a/b/c/d/../.."),
        (r"/a/b/c", r"/a/b"),
        (r"/a/b/c", r"/d/q/f"),
        (r"/a/b/../d/c", r"/a/d/c.txt"),
        (r"/a/b/../d/c", r"/a/b/../b/c/d/../e"),
        (r"/a/b/../d/c.txt", r"/a/d/c")
    ])
    def test_notIsPathInLocation(self, location, subfolder):
        assert not TrustBasics.isPathInLocation(location, subfolder)
