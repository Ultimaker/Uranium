# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import platform
import unittest
from unittest import TestCase
from unittest.mock import patch, PropertyMock
import tempfile
import pytest

from UM.Resources import Resources, ResourceTypeError, UnsupportedStorageTypeError


class TestResources(TestCase):

    #
    # getConfigStorageRootPath() tests
    #
    @unittest.skipIf(platform.system() != "Windows", "Not on Windows")
    def test_getConfigStorageRootPath_Windows(self):
        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.getenv("APPDATA")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    @unittest.skipIf(platform.system() != "Linux", "Not on linux")
    def test_getConfigStorageRootPath_Linux(self):
        # no XDG_CONFIG_HOME defined
        if "XDG_CONFIG_HOME" in os.environ:
            del os.environ["XDG_CONFIG_HOME"]
        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/.config")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

        # XDG_CONFIG_HOME defined
        os.environ["XDG_CONFIG_HOME"] = "/tmp"
        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = "/tmp"
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    @unittest.skipIf(platform.system() != "Darwin", "Not on mac")
    def test_getConfigStorageRootPath_Mac(self):
        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/Library/Application Support")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    @unittest.skipIf(platform.system() != "Windows", "Not on Windows")
    def test_getDataStorageRootPath_Windows(self):
        data_root_path = Resources._getDataStorageRootPath()
        self.assertIsNone(data_root_path, "expected None, got %s" % data_root_path)

    @unittest.skipIf(platform.system() != "Linux", "Not on linux")
    def test_getDataStorageRootPath_Linux(self):
        # no XDG_CONFIG_HOME defined
        if "XDG_DATA_HOME" in os.environ:
            del os.environ["XDG_DATA_HOME"]
        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = os.path.expanduser("~/.local/share")
        self.assertEqual(expected_data_root_path, data_root_path,
                         "expected %s, got %s" % (expected_data_root_path, data_root_path))

        # XDG_CONFIG_HOME defined
        os.environ["XDG_DATA_HOME"] = "/tmp"
        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = "/tmp"
        self.assertEqual(expected_data_root_path, data_root_path,
                         "expected %s, got %s" % (expected_data_root_path, data_root_path))

    @unittest.skipIf(platform.system() != "Darwin", "Not on mac")
    def test_getDataStorageRootPath_Mac(self):
        data_root_path = Resources._getDataStorageRootPath()
        self.assertIsNone(data_root_path, "expected None, got %s" % data_root_path)

    @unittest.skipIf(platform.system() != "Windows", "Not on Windows")
    def test_getCacheStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.getenv("LOCALAPPDATA")
        self.assertEqual(expected_cache_root_path, cache_root_path,
                         "expected %s, got %s" % (expected_cache_root_path, cache_root_path))

    @unittest.skipIf(platform.system() != "Linux", "Not on linux")
    def test_getCacheStorageRootPath_Linux(self):
        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.path.expanduser("~/.cache")
        self.assertEqual(expected_cache_root_path, cache_root_path,
                         "expected %s, got %s" % (expected_cache_root_path, cache_root_path))

    @unittest.skipIf(platform.system() != "Darwin", "Not on mac")
    def test_getCacheStorageRootPath_Mac(self):
        cache_root_path = Resources._getCacheStorageRootPath()
        self.assertIsNone("expected None, got %s" % cache_root_path)

    @unittest.skipIf(platform.system() != "Linux", "Not on linux")
    def test_getPossibleConfigStorageRootPathList_Linux(self):
        # We didn't add any paths, so it will use defaults
        assert Resources._getPossibleConfigStorageRootPathList() == ['/tmp/test']

    @unittest.skipIf(platform.system() != "Linux", "Not on linux")
    def test_getPossibleDataStorageRootPathList_Linux(self):
        # We didn't add any paths, so it will use defaults
        assert Resources._getPossibleDataStorageRootPathList() == ['/tmp/test']

    def test_factoryReset(self):
        # FIXME: This is a temporary workaround. A proper fix should be to make the home directory configurable so a
        #        unique temporary directory can be used for each test and it can removed afterwards.
        # HACK: Record the number of files and directories in the data storage directory before the factory reset,
        # so after the reset, we can compare if there's a new ZIP file being created. Note that this will not always
        # work, especially when there are multiple tests running on the same host at the same time.
        original_filenames = os.listdir(os.path.dirname(Resources.getDataStoragePath()))

        Resources.factoryReset()
        # Check if the data is deleted!
        assert len(os.listdir(Resources.getDataStoragePath())) == 0

        # The data folder should still be there, but it should also have created a zip with the data it deleted.
        new_filenames = os.listdir(os.path.dirname(Resources.getDataStoragePath()))
        assert len(new_filenames) - len(original_filenames) == 1

        # Clean up after our ass.
        folder = os.path.dirname(Resources.getDataStoragePath())
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                os.unlink(file_path)
            except:
                pass
        folder = os.path.dirname(Resources.getDataStoragePath())
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                os.unlink(file_path)
            except:
                pass

    def test_copyLatestDirsIfPresent(self):
        # Just don't fail.
        Resources._copyLatestDirsIfPresent()

    @unittest.skipIf(platform.system() != "Linux", "Not on linux")
    def test_getStoragePathForType_Linux(self):
        with pytest.raises(ResourceTypeError):
            # No types have been added, so this should break!
            Resources.getAllResourcesOfType(0)
        with pytest.raises(UnsupportedStorageTypeError):
            # We still haven't added it, so it should fail (again)
            Resources.getStoragePathForType(0)

        Resources.addStorageType(0, "/test")
        assert Resources.getStoragePathForType(0) == "/test"

    def test_getAllResourcesOfType(self):
        resouce_folder = tempfile.mkdtemp("test_folder_origin")
        resource_file = tempfile.mkstemp(dir=str(resouce_folder))
        Resources.addStorageType(111, resouce_folder)
        assert Resources.getAllResourcesOfType(111) == [resource_file[1]]

    def test_copyVersionFolder(self):

        import os
        folder_to_copy = tempfile.mkdtemp("test_folder_origin")
        file_to_copy = tempfile.mkstemp(dir=str(folder_to_copy))

        folder_to_move_to = tempfile.mkdtemp("test_folder_destination")

        Resources.copyVersionFolder(str(folder_to_copy), str(folder_to_move_to) + "/target")
        # We put a temp file in the folder to copy, check if it arrived there.
        assert len(os.listdir(str(folder_to_move_to) + "/target")) == 1

    # The app version is "dev", and this is considered as the latest version possible. It will upgrade from the highest
    # "<major>.<minor>" directory that's available.
    def test_findLatestDirInPathsDevAppVersion(self):
        test_folder = tempfile.mkdtemp("test_folder")
        for folder in ("whatever", "2.1", "3.4", "4.2", "5.1", "10.2", "50.7"):
            os.mkdir(os.path.join(test_folder, folder))

        with patch("UM.Resources.Resources.ApplicationVersion", new_callable = PropertyMock(return_value = "dev")):
            # We should obviously find the folder that was created by means of the ApplicationVersion.
            assert Resources._findLatestDirInPaths([test_folder]) == os.path.join(test_folder, "50.7")

    # Tests _findLatestDirInPaths() with a normal application version, that is a version like "<major>.<minor>".
    # In this case, it should get the highest available "<major>.<minor>" directory but no higher than the application
    # version itself.
    def test_findLatestDirInPathsNormalAppVersion(self):
        test_folder = tempfile.mkdtemp("test_folder")
        for folder in ("whatever", "2.1", "3.4", "4.2", "5.1", "10.2", "50.7"):
            os.mkdir(os.path.join(test_folder, folder))

        with patch("UM.Resources.Resources.ApplicationVersion", new_callable = PropertyMock(return_value = "4.3")):
            # We should obviously find the folder that was created by means of the ApplicationVersion.
            assert Resources._findLatestDirInPaths([test_folder]) == os.path.join(test_folder, "4.2")

    # In this case, our app version is 4.3, but all the available directories do not have names "<major>.<minor>".
    # _findLatestDirInPaths() should return None.
    def test_findLatestDirInPathsNormalAppVersionNoValidUpgrade(self):
        test_folder = tempfile.mkdtemp("test_folder")
        for folder in ("whatever1", "whatever2", "foobar1", "dev", "master", "test"):
            os.mkdir(os.path.join(test_folder, folder))

        with patch("UM.Resources.Resources.ApplicationVersion", new_callable = PropertyMock(return_value = "4.3")):
            # There is no folder that matches what we're looking for!
            assert Resources._findLatestDirInPaths([test_folder]) is None

    # In this case, our app version is 4.3, but all there's no available directory named as "<major>.<minor>".
    # _findLatestDirInPaths() should return None.
    def test_findLatestDirInPathsNormalAppVersionEmptySearchFolder(self):
        test_folder = tempfile.mkdtemp("test_folder")

        with patch("UM.Resources.Resources.ApplicationVersion", new_callable = PropertyMock(return_value = "4.3")):
            # There is no folder that matches what we're looking for!
            assert Resources._findLatestDirInPaths([test_folder]) is None

    def test_addRemoveStorageType(self):
        Resources.addStorageType(9901, "YAY")
        Resources.addType(9902, "whoo")
        Resources.addStorageType(100, "herpderp")

        with pytest.raises(ResourceTypeError):
            # We can't add the same type again
            Resources.addStorageType(9901, "nghha")

        Resources.removeType(9001)
        Resources.removeType(9902)

        with pytest.raises(ResourceTypeError):
            # We can't do that, since it's in the range of user types.
            Resources.removeType(100)

        with pytest.raises(ResourceTypeError):
            # We can't do that, since it's in the range of user types.
            Resources.addType(102, "whoo")

