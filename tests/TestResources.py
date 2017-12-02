# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import platform
from unittest import TestCase

from UM.Resources import Resources


class TestResources(TestCase):

    #
    # getConfigStorageRootPath() tests
    #
    def test_getConfigStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.getenv("APPDATA")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    def test_getConfigStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

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

    def test_getConfigStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/Library/Application Support")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    #
    # getDataStorageRootPath() tests
    #
    def test_getDataStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        data_root_path = Resources._getDataStorageRootPath()
        self.assertIsNone(data_root_path, "expected None, got %s" % data_root_path)

    def test_getDataStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

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

    def test_getDataStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        data_root_path = Resources._getDataStorageRootPath()
        self.assertIsNone(data_root_path, "expected None, got %s" % data_root_path)

    #
    # getCacheStorageRootPath() tests
    #
    def test_getCacheStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.getenv("LOCALAPPDATA")
        self.assertEqual(expected_cache_root_path, cache_root_path,
                         "expected %s, got %s" % (expected_cache_root_path, cache_root_path))

    def test_getCacheStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.path.expanduser("~/.cache")
        self.assertEqual(expected_cache_root_path, cache_root_path,
                         "expected %s, got %s" % (expected_cache_root_path, cache_root_path))

    def test_getCacheStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        cache_root_path = Resources._getCacheStorageRootPath()
        self.assertIsNone("expected None, got %s" % cache_root_path)
