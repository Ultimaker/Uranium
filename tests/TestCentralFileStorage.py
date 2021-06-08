# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import hashlib  # To give a hash to the central file storage.
import os  # To deal with test files.
import pytest  # The test runner.
import shutil  # To clean up after the test.
import unittest.mock  # To mock the Resources class.

from UM.CentralFileStorage import CentralFileStorage  # The class under test.
from UM.Version import Version  # Storing files of different versions.

TEST_FILE_PATH = "test_file.txt"
TEST_FILE_CONTENTS = b"May thy PLA floweth into all the right spots, and none other."
TEST_FILE_HASH = hashlib.sha256(TEST_FILE_CONTENTS).hexdigest()
TEST_FILE_PATH2 = "test_file2.txt"
TEST_FILE_CONTENTS2 = b"May all PVA dissolveth to the snotty goo from wence it came, for it be its natural state of being."
TEST_FILE_HASH2 = hashlib.sha256(TEST_FILE_CONTENTS2).hexdigest()

def setup_function():
    with open(TEST_FILE_PATH, "wb") as f:
        f.write(TEST_FILE_CONTENTS)
    with open(TEST_FILE_PATH2, "wb") as f:
        f.write(TEST_FILE_CONTENTS2)

def teardown_function():
    try:
        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)
        if os.path.exists(TEST_FILE_PATH2):
            os.remove(TEST_FILE_PATH2)
        if os.path.exists("test_central_storage"):
            shutil.rmtree("test_central_storage")
    except EnvironmentError:
        pass

def test_storeRetrieve():
    """
    Basic store-retrieve loop test.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        CentralFileStorage.store(TEST_FILE_PATH, "myfile")
        stored_path = CentralFileStorage.retrieve("myfile", TEST_FILE_HASH)
    assert not os.path.exists(TEST_FILE_PATH)
    assert os.path.exists(stored_path)
    assert open(stored_path, "rb").read() == TEST_FILE_CONTENTS

def test_storeNonExistent():
    """
    Tests storing a file that doesn't exist.

    The storage is expected to fail silently, leaving just a debug statement that it was already stored.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        CentralFileStorage.store("non_existent_file.txt", "my_non_existent_file")  # Shouldn't raise error.

def test_storeDuplicate():
    """
    Tests storing a file twice.

    The storage should make the files unique, i.e. remove the duplicate.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        shutil.copy(TEST_FILE_PATH, TEST_FILE_PATH + ".copy.txt")
        CentralFileStorage.store(TEST_FILE_PATH, "myfile")
        CentralFileStorage.store(TEST_FILE_PATH + ".copy.txt", "myfile")  # Shouldn't raise error. File contents are identical.
        assert not os.path.exists(TEST_FILE_PATH + ".copy.txt")  # Duplicate must be removed.

def test_storeConflict():
    """
    Tests storing two different files under the same ID/version.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        CentralFileStorage.store(TEST_FILE_PATH, "myfile")
        pytest.raises(FileExistsError, lambda: CentralFileStorage.store(TEST_FILE_PATH2, "myfile"))

def test_storeVersions():
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        CentralFileStorage.store(TEST_FILE_PATH, "myfile", Version("1.0.0"))
        CentralFileStorage.store(TEST_FILE_PATH2, "myfile", Version("1.1.0"))
        stored_path1 = CentralFileStorage.retrieve("myfile", TEST_FILE_HASH, Version("1.0.0"))
        stored_path2 = CentralFileStorage.retrieve("myfile", TEST_FILE_HASH2, Version("1.1.0"))
    assert stored_path1 != stored_path2
    assert open(stored_path1, "rb").read() == TEST_FILE_CONTENTS
    assert open(stored_path2, "rb").read() == TEST_FILE_CONTENTS2

def test_retrieveNonExistent():
    """
    Tests retrieving a file that is not stored in the central location.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        pytest.raises(FileNotFoundError, lambda: CentralFileStorage.retrieve("non_existent_file", "0123456789ABCDEF"))

def test_retrieveWrongHashOnEnterprise():
    """
    Tests retrieving a file that has a wrong hash.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        CentralFileStorage.setIsEnterprise(True)
        CentralFileStorage.store(TEST_FILE_PATH, "myfile")
        pytest.raises(IOError, lambda: CentralFileStorage.retrieve("myfile", TEST_FILE_HASH2))
