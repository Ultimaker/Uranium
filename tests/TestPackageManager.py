# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest
import unittest.mock
from unittest.mock import MagicMock

from UM.PackageManager import PackageManager


@unittest.mock.patch.object(PackageManager, "__init__", lambda *args, **kwargs: None)
def test_comparePackageVersions():
    test_cases = [
        # same versions
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "1.0"},
         "info_dict2": {"sdk_version": "1",
                        "package_version": "1.0"},
         "expected_result": 0},

        # same package versions, different sdk versions
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "1.0"},
         "info_dict2": {"sdk_version": "3",
                        "package_version": "1.0"},
         "expected_result": -1},

        # different package versions, same sdk versions
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "3.0"},
         "info_dict2": {"sdk_version": "1",
                        "package_version": "1.0"},
         "expected_result": 1},

        # different package versions, different sdk versions  #1
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "3.0"},
         "info_dict2": {"sdk_version": "3",
                        "package_version": "1.0"},
         "expected_result": -1},

        # different package versions, different sdk versions  #2
        {"info_dict1": {"sdk_version": "7",
                        "package_version": "3.0"},
         "info_dict2": {"sdk_version": "3",
                        "package_version": "6.0"},
         "expected_result": -1},
    ]

    package_manager = PackageManager()
    for test_case_dict in test_cases:
        info_dict1 = test_case_dict["info_dict1"]
        info_dict2 = test_case_dict["info_dict2"]
        expected_result = test_case_dict["expected_result"]

        assert expected_result == package_manager._comparePackageVersions(info_dict1, info_dict2)


def test_emptyInit():
    manager = PackageManager(MagicMock())

    assert not manager.getAllInstalledPackageIDs()
    assert not manager.getAllInstalledPackagesInfo()

    manager.installedPackagesChanged = MagicMock()
    manager.removePackage("packageThatDoesNotExist")
    assert manager.installedPackagesChanged.emit().call_count == 0

    with pytest.raises(FileNotFoundError):
        assert manager.getPackageLicense("FileThatDoesntExist.package") == {}

    assert manager.getPackageFiles("packageThatDoesNotExist") == []

    assert manager.getPackageContainerIds("packageThatDoesNotExist") == []

