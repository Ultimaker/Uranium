# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import hashlib  # To give a hash to the central file storage.
import os  # To deal with test files.
import pytest  # The test runner.
import shutil  # To clean up after the test.
import unittest.mock  # To mock the Resources class.

from UM.CentralFileStorage import CentralFileStorage  # The class under test.

TEST_FILE_PATH = "test_file.txt"
TEST_FILE_CONTENTS = b"May thy PLA floweth into all the right spots, and none other."
TEST_FILE_HASH = hashlib.sha256(TEST_FILE_CONTENTS).hexdigest()

def setup_function():
    with open(TEST_FILE_PATH, "wb") as f:
        f.write(TEST_FILE_CONTENTS)

def teardown_function():
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    if os.path.exists("test_central_storage"):
        shutil.rmtree("test_central_storage")

def test_storeRetrieve():
    """
    Basic store-retrieve loop test.
    """
    with unittest.mock.patch("UM.Resources.Resources.getDataStoragePath", lambda: "test_central_storage/4.9"):
        CentralFileStorage.store(TEST_FILE_PATH, "myfile")
        CentralFileStorage.retrieve("myfile", TEST_FILE_HASH)
