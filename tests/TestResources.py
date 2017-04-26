# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import sys
import os
import platform
from unittest import TestCase

from PyQt5.QtCore import QCoreApplication

from UM.Resources import Resources


class TestResources(TestCase):
    def setUp(self):
        self.application = QCoreApplication(sys.argv)
        self.application.setApplicationName("test")

    #
    # getConfigStorageRootPath() tests
    #
    def test_getConfigStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.join(os.getenv("APPDATA"), "test")
        self.assertEqual(expected_config_root_path, config_root_path)

    def test_getConfigStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/.config/test")
        self.assertEqual(expected_config_root_path, config_root_path)

    def test_getConfigStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/Library/Preferences/test")
        self.assertEqual(expected_config_root_path, config_root_path)

    #
    # getDataStorageRootPath() tests
    #
    def test_getDataStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = os.path.join(os.getenv("APPDATA"), "test")
        self.assertEqual(expected_data_root_path, data_root_path)

    def test_getDataStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = os.path.expanduser("~/.local/share/test")
        self.assertEqual(expected_data_root_path, data_root_path)

    def test_getDataStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = os.expanduser("~/Library/Application Support/test")
        self.assertEqual(expected_data_root_path, data_root_path)

    #
    # getCacheStorageRootPath() tests
    #
    def test_getCacheStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.path.join(os.getenv("LOCALAPPDATA"), "test", "cache")
        self.assertEqual(expected_cache_root_path, cache_root_path)

    def test_getCacheStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.path.expanduser("~/.cache/test")
        self.assertEqual(expected_cache_root_path, cache_root_path)

    def test_getCacheStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.path.expanduser("~/Library/Caches/test")
        self.assertIsNone("expected None, got %s" % cache_root_path)
