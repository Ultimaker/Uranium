# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import os
import pytest
import unittest.mock
from unittest.mock import MagicMock, patch

from UM.PackageManager import PackageManager
from UM.Version import Version

test_package_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/UnitTestPackage.package")


#@unittest.mock.patch.object(PackageManager, "__init__", lambda *args, **kwargs: None)
def test_shouldInstallCandidate():

    app_sdk = "2.2.3"
    test_cases = [

        # same sdk version, newer package
        {"candidate_dict": {"sdk_version": app_sdk,
                            "package_version": "1.1"},
         "bundle_dict": {"sdk_version": app_sdk,
                         "package_version": "1.0"},
         "expected_result": True},

        # compatible sdk version, newer package
        {"candidate_dict": {"sdk_version": "2.1.1",
                            "package_version": "1.1"},
         "bundle_dict": {"sdk_version": app_sdk,
                         "package_version": "1.0"},
         "expected_result": True},

        # incompatible sdk version (older)
        {"candidate_dict": {"sdk_version": "1.0.0",
                        "package_version": "1.1"},
         "bundle_dict": {"sdk_version": app_sdk,
                        "package_version": "1.0"},
         "expected_result": False},

        # incompatible sdk version (newer, same major)
        {"candidate_dict": {"sdk_version": "2.4.0",
                            "package_version": "1.1"},
         "bundle_dict": {"sdk_version": app_sdk,
                         "package_version": "1.0"},
         "expected_result": False},

        # same package versions, same sdk versions
        {"candidate_dict": {"sdk_version": app_sdk,
                            "package_version": "1.0"},
         "bundle_dict": {"sdk_version": app_sdk,
                         "package_version": "1.0"},
         "expected_result": False},  # not an upgrade

        # same package versions, compatible sdk versions
        {"candidate_dict": {"sdk_version": "2.1.0",
                        "package_version": "1.0"},
         "bundle_dict": {"sdk_version": "2.2.3",
                        "package_version": "1.0"},
         "expected_result": False},  # not an upgrade

        # older package versions, same sdk versions
        {"candidate_dict": {"sdk_version": app_sdk,
                        "package_version": "4.1"},
         "bundle_dict": {"sdk_version": app_sdk,
                        "package_version": "4.2"},
         "expected_result": False},
    ]

    app = MagicMock()
    app.getAPIVersion.return_value = Version(app_sdk)
    package_manager = PackageManager(app)
    for test_case_dict in test_cases:
        candidate_dict = test_case_dict["candidate_dict"]
        bundle_dict = test_case_dict["bundle_dict"]
        expected_result = test_case_dict["expected_result"]

        assert expected_result == package_manager._shouldInstallCandidate(candidate_dict, bundle_dict)


def test_getLicense():
    manager = PackageManager(MagicMock())
    assert manager.getPackageLicense(test_package_path) == "Do whatever you want with this.\n"


def test_installAndRemovePackage():
    mock_application = MagicMock()
    mock_registry = MagicMock()
    mock_registry.isActivePlugin = MagicMock(return_value = False)
    mock_application.getPluginRegistry = MagicMock(return_value = mock_registry)
    manager = PackageManager(mock_application)
    manager.installedPackagesChanged = MagicMock()
    package_id = manager.installPackage(test_package_path)
    assert manager.installedPackagesChanged.emit.call_count == 1
    assert manager.isPackageInstalled("UnitTestPackage")
    assert package_id == "UnitTestPackage"

    info = manager.getInstalledPackageInfo("UnitTestPackage")
    assert info["author"]["author_id"] == "nallath"
    assert info["display_name"] == "UnitTestPackage"

    # We don't want the package to be purged. We need that package for the other tests!
    with patch("os.remove", MagicMock()):
        manager._installPackage({"package_info": info, "filename": test_package_path})

    assert "UnitTestPackage" in manager.getAllInstalledPackageIDs()
    assert manager.isUserInstalledPackage("UnitTestPackage")
    assert manager.getAllInstalledPackagesInfo()["plugin"][0]["display_name"] == "UnitTestPackage"
    manager.initialize()
    # Now to remove the package again!
    manager.removePackage("UnitTestPackage")
    assert manager.installedPackagesChanged.emit.call_count == 2


def test_getPackageInfo():
    manager = PackageManager(MagicMock())
    info = manager.getPackageInfo(test_package_path)

    assert info["author"]["author_id"] == "nallath"
    assert info["display_name"] == "UnitTestPackage"


def test_emptyInit():
    manager = PackageManager(MagicMock())

    assert not manager.getAllInstalledPackageIDs()
    assert not manager.getAllInstalledPackagesInfo()

    manager.installedPackagesChanged = MagicMock()
    manager.removePackage("packageThatDoesNotExist")
    assert manager.installedPackagesChanged.emit.call_count == 0

    assert manager.getBundledPackageInfo("packageThatDoesNotExist") is None

    with pytest.raises(FileNotFoundError):
        assert manager.getPackageLicense("FileThatDoesntExist.package") == {}

    assert manager.getPackageFiles("packageThatDoesNotExist") == []

    assert manager.getPackageContainerIds("packageThatDoesNotExist") == []


class TestAddAvailablePackageVersion:
    def test_addNewVersionThatCanUpdate(self):
        manager = PackageManager(MagicMock())
        manager.checkIfPackageCanUpdate = MagicMock(return_value = True)
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))

        assert manager.packagesWithUpdate == {"beep"}

    def test_addNewVersionThatCantUpdate(self):
        manager = PackageManager(MagicMock())
        manager.checkIfPackageCanUpdate = MagicMock(return_value=False)
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))

        assert manager.packagesWithUpdate == set()

    def test_addMultipleVersions(self):
        manager = PackageManager(MagicMock())
        manager.checkIfPackageCanUpdate = MagicMock(return_value=True)
        manager.addAvailablePackageVersion("beep", Version("1.2.0"))
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))

        assert manager.packagesWithUpdate == {"beep"}


class TestCheckIfPackageCanUpdate:
    def test_noAvailableVersions(self):
        manager = PackageManager(MagicMock())
        assert manager.checkIfPackageCanUpdate("beep") is False

    def test_availableVersionNotInstalledOrBundled(self):
        manager = PackageManager(MagicMock())
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))

        # Even though we have a known package version, it's not installed / bundled, so we cant update
        assert manager.checkIfPackageCanUpdate("beep") is False

    def test_olderVersionIsBundled(self):
        manager = PackageManager(MagicMock())
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))
        manager._bundled_package_dict = {"beep": {"package_info": {"package_version": "0.9.0"}}}

        assert manager.checkIfPackageCanUpdate("beep") is True

    def test_newerVersionIsBundled(self):
        manager = PackageManager(MagicMock())
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))
        manager._bundled_package_dict = {"beep": {"package_info": {"package_version": "1.9.0"}}}

        assert manager.checkIfPackageCanUpdate("beep") is False

    def test_olderVersionIsInstalled(self):
        manager = PackageManager(MagicMock())
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))
        manager._installed_package_dict = {"beep": {"package_info": {"package_version": "0.9.0"}}}

        assert manager.checkIfPackageCanUpdate("beep") is True

    def test_newerVersionIsInstalled(self):
        manager = PackageManager(MagicMock())
        manager.addAvailablePackageVersion("beep", Version("1.0.0"))
        manager._installed_package_dict = {"beep": {"package_info": {"package_version": "1.9.1"}}}

        assert manager.checkIfPackageCanUpdate("beep") is False


def test_removeAllScheduledPackages():
    manager = PackageManager(MagicMock())
    manager._purgePackage = MagicMock()

    manager._to_remove_package_set = {"beep"}
    manager._installed_package_dict = {"beep": {}}
    manager._removeAllScheduledPackages()
    assert manager._to_remove_package_set == set()


def test_removeAllScheduledPackagesWithException():
    manager = PackageManager(MagicMock())
    manager._purgePackage = MagicMock(side_effect = Exception)
    manager._installed_package_dict = {"beep": {}}
    manager._to_remove_package_set = {"beep"}

    manager._removeAllScheduledPackages()
    assert manager._to_remove_package_set == {"beep"}