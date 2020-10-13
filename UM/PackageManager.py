# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os
import shutil
import tempfile
import urllib.parse  # For interpreting escape characters using unquote_plus.
import zipfile
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Set, Tuple, cast, TYPE_CHECKING

from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QUrl, pyqtProperty

from UM import i18nCatalog
from UM.Logger import Logger
from UM.Message import Message
from UM.MimeTypeDatabase import MimeTypeDatabase  # To get the type of container we're loading.
from UM.Resources import Resources
from UM.Signal import Signal
from UM.Version import Version as UMVersion

catalog = i18nCatalog("uranium")

if TYPE_CHECKING:
    from UM.Qt.QtApplication import QtApplication


class PackageManager(QObject):
    Version = 1

    def __init__(self, application: "QtApplication", parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

        self._application = application
        self._container_registry = self._application.getContainerRegistry()
        self._plugin_registry = self._application.getPluginRegistry()

        # JSON files that keep track of all installed packages.
        self._user_package_management_file_path = None  # type: Optional[str]
        self._bundled_package_management_file_paths = []  # type: List[str]
        for search_path in Resources.getAllPathsForType(Resources.BundledPackages):
            if not os.path.isdir(search_path):
                continue

            # Load all JSON files that are located in the bundled_packages directory.
            for file_name in os.listdir(search_path):
                if not file_name.endswith(".json"):
                    continue
                file_path = os.path.join(search_path, file_name)
                if not os.path.isfile(file_path):
                    continue
                self._bundled_package_management_file_paths.append(file_path)
                Logger.log("i", "Found bundled packages JSON file: {location}".format(location = file_path))

        for search_path in (Resources.getDataStoragePath(), Resources.getConfigStoragePath()):
            candidate_user_path = os.path.join(search_path, "packages.json")
            if os.path.exists(candidate_user_path):
                self._user_package_management_file_path = candidate_user_path
        if self._user_package_management_file_path is None:  # Doesn't exist yet.
            self._user_package_management_file_path = os.path.join(Resources.getDataStoragePath(), "packages.json")

        self._installation_dirs_dict = {"plugins": os.path.abspath(Resources.getStoragePath(Resources.Plugins))}  # type: Dict[str, str]

        self._bundled_package_dict = {}  # type: Dict[str, Dict[str, Any]] # A dict of all bundled packages
        self._installed_package_dict = {}  # type: Dict[str, Dict[str, Any]] # A dict of all installed packages
        self._to_remove_package_set = set()  # type: Set[str] # A set of packages that need to be removed at the next start
        self._to_install_package_dict = {}  # type: Dict[str, Dict[str, Any]]  # A dict of packages that need to be installed at the next start
        self._dismissed_packages = set()    # type: Set[str] # A set of packages that are dismissed by the user

        # There can be plugins that provide remote packages (and thus, newer / different versions for a package).
        self._available_package_versions = {}  # type: Dict[str, Set[UMVersion]]

        self._packages_with_update_available = set()  # type: Set[str]

    packageInstalled = Signal()  # Emits the package_id (str) of an installed package
    installedPackagesChanged = pyqtSignal()  # Emitted whenever the installed packages collection have been changed.
    packagesWithUpdateChanged = pyqtSignal()

    def initialize(self) -> None:
        self._loadManagementData()
        self._removeAllScheduledPackages()
        self._installAllScheduledPackages()

    # Notify the Package manager that there is an alternative version for a given package.
    def addAvailablePackageVersion(self, package_id: str, version: "UMVersion") -> None:
        if package_id not in self._available_package_versions:
            self._available_package_versions[package_id] = set()
        self._available_package_versions[package_id].add(version)

        if self.checkIfPackageCanUpdate(package_id):
            self._packages_with_update_available.add(package_id)
            self.packagesWithUpdateChanged.emit()

    @pyqtProperty("QStringList", notify = packagesWithUpdateChanged)
    def packagesWithUpdate(self) -> Set[str]:
        return self._packages_with_update_available

    def setPackagesWithUpdate(self, packages: Set[str]):
        """Alternative way of setting the available package updates without having to check all packages in the
        cloud. """

        self._packages_with_update_available = packages
        self.packagesWithUpdateChanged.emit()

    def isPackageCompatible(self, package_api_version: UMVersion) -> bool:
        """
        Check whether an API version is compatible with the application's API
        version.
        :param package_api_version: The API version to check.
        :return: ``True`` if packages with this API version are compatible, or
        ``False`` if they are not.
        """
        app_api_version = self._application.getAPIVersion()

        if app_api_version.getMajor() != package_api_version.getMajor():
            return False

        # minor versions are backwards compatible
        if app_api_version.getMinor() < package_api_version.getMinor():
            return False

        return True

    def checkIfPackageCanUpdate(self, package_id: str) -> bool:
        available_versions = self._available_package_versions.get(package_id)

        if available_versions is None:
            return False

        current_version = None

        bundled_package_dict = self._bundled_package_dict.get(package_id)
        if bundled_package_dict is not None:
            current_version = UMVersion(bundled_package_dict["package_info"]["package_version"])

        installed_package_dict = self._installed_package_dict.get(package_id)
        if installed_package_dict is not None:
            current_version = UMVersion(installed_package_dict["package_info"]["package_version"])

            # One way to check if the package has been updated in looking at the to_install information in the packages.json
            to_install_package_dict = self._to_install_package_dict.get(package_id)
            if to_install_package_dict is not None: # If it's marked as to_install, that means package will be installed upon restarting
                    return False

        if current_version is not None:
            for available_version in available_versions:
                if current_version < available_version:
                    # Stop looking, there is at least one version that is higher.
                    return True
        return False

    # (for initialize) Loads the package management file if exists
    def _loadManagementData(self) -> None:
        # The bundled package management file should always be there
        if len(self._bundled_package_management_file_paths) == 0:
            Logger.log("w", "Bundled package management files could not be found!")
            return
        # Load the bundled packages:
        self._bundled_package_dict = {}
        for search_path in self._bundled_package_management_file_paths:
            try:
                with open(search_path, "r", encoding = "utf-8") as f:
                    self._bundled_package_dict.update(json.load(f))
                    Logger.log("i", "Loaded bundled packages data from %s", search_path)
            except UnicodeDecodeError:
                Logger.logException("e", "Can't decode package management files. File is corrupt.")
                return

        # Need to use the file lock here to prevent concurrent I/O from other processes/threads
        container_registry = self._application.getContainerRegistry()
        with container_registry.lockFile():
            try:
                # Load the user packages:
                with open(cast(str, self._user_package_management_file_path), "r", encoding = "utf-8") as f:
                    try:
                        management_dict = json.load(f)
                    except (JSONDecodeError, UnicodeDecodeError):
                        # The file got corrupted, ignore it. This happens extremely infrequently.
                        # The file will get overridden once a user downloads something.
                        return
                    self._installed_package_dict = management_dict.get("installed", {})
                    self._to_remove_package_set = set(management_dict.get("to_remove", []))
                    self._to_install_package_dict = management_dict.get("to_install", {})
                    self._dismissed_packages = set(management_dict.get("dismissed", []))
                    Logger.log("i", "Loaded user packages management file from %s", self._user_package_management_file_path)
            except FileNotFoundError:
                Logger.log("i", "User package management file %s doesn't exist, do nothing", self._user_package_management_file_path)
                return

        # For packages that become bundled in the new releases, but a lower version was installed previously, we need
        # to remove the old lower version that's installed in the user's folder.
        for package_id, installed_package_dict in self._installed_package_dict.items():
            bundled_package_dict = self._bundled_package_dict.get(package_id)
            if bundled_package_dict is None:
                continue

            should_install = self._shouldInstallCandidate(installed_package_dict["package_info"],
                                                  bundled_package_dict["package_info"])
            # The bundled package is newer
            if not should_install:
                self._to_remove_package_set.add(package_id)
                continue

        # Also check the to-install packages to avoid installing packages that have a lower version than the bundled
        # ones.
        to_remove_package_ids = set()
        for package_id, to_install_package_dict in self._to_install_package_dict.items():
            bundled_package_dict = self._bundled_package_dict.get(package_id)
            if bundled_package_dict is None:
                continue

            should_install = self._shouldInstallCandidate(to_install_package_dict["package_info"],
                                                  bundled_package_dict["package_info"])
            # The bundled package is newer
            if not should_install:
                Logger.info(
                    "Ignoring package {} since it's sdk or package version is lower than the bundled package",
                    package_id
                )
                to_remove_package_ids.add(package_id)
                continue
        for package_id in to_remove_package_ids:
            del self._to_install_package_dict[package_id]

    # Compares the SDK versions and the package versions of the two given package info dicts.
    # Returns True if the candidate is preferred over the base
    #  - The package with the higher SDK version is considered having the higher version number. If they are the same,
    #  - if the based package version is greater than or equal to the given package, -1 is returned. Otherwise, 1.
    def _shouldInstallCandidate(self, candidate_dict: Dict[str, Any], base_dict: Dict[str, Any]) -> bool:
        # If the base version has a higher SDK version, use the based version by removing the candidate one.
        sdk_version_candidate = UMVersion(candidate_dict["sdk_version"])
        if not self.isPackageCompatible(sdk_version_candidate):
            return False

        # Remove the package with the old version to favour the newer based version.
        version_candidate = UMVersion(candidate_dict["package_version"])
        version_base = UMVersion(base_dict["package_version"])
        if version_candidate <= version_base:
            return False

        return True

    def _saveManagementData(self) -> None:
        # Need to use the file lock here to prevent concurrent I/O from other processes/threads
        container_registry = self._application.getContainerRegistry()
        with container_registry.lockFile():
            try:
                with open(cast(str,self._user_package_management_file_path), "w", encoding = "utf-8") as f:
                    data_dict = {"version": PackageManager.Version,
                                 "installed": self._installed_package_dict,
                                 "to_remove": list(self._to_remove_package_set),
                                 "to_install": self._to_install_package_dict,
                                 "dismissed": list(self._dismissed_packages)}
                    json.dump(data_dict, f, sort_keys = True, indent = 4)
                    Logger.log("i", "Package management file %s was saved", self._user_package_management_file_path)
            except EnvironmentError as e:  # Can't save for whatever reason (permissions, missing directory, hard drive full, etc).
                Logger.error("Unable to save package management file to {path}: {err}".format(path = self._user_package_management_file_path, err = str(e)))

    # (for initialize) Removes all packages that have been scheduled to be removed.
    def _removeAllScheduledPackages(self) -> None:
        remove_failures = set()
        for package_id in self._to_remove_package_set:
            try:
                self._purgePackage(package_id)
                del self._installed_package_dict[package_id]
            except:
                remove_failures.add(package_id)

        if remove_failures:
            message = Message(catalog.i18nc("@error:uninstall",
                                            "There were some errors uninstalling the following packages:\n{packages}".format(
                                            packages = "- " + "\n- ".join(remove_failures))),
                              title = catalog.i18nc("@info:title", "Uninstalling errors"))
            message.show()

        self._to_remove_package_set = remove_failures
        self._saveManagementData()

    # (for initialize) Installs all packages that have been scheduled to be installed.
    def _installAllScheduledPackages(self) -> None:
        while self._to_install_package_dict:
            package_id, package_info = list(self._to_install_package_dict.items())[0]
            self._installPackage(package_info)
            del self._to_install_package_dict[package_id]
            self._saveManagementData()

    def getBundledPackageInfo(self, package_id: str) -> Optional[Dict[str, Any]]:
        package_info = None
        if package_id in self._bundled_package_dict:
            package_info = self._bundled_package_dict[package_id]["package_info"]
        return package_info

    # Checks the given package is installed. If so, return a dictionary that contains the package's information.
    def getInstalledPackageInfo(self, package_id: str) -> Optional[Dict[str, Any]]:
        if package_id in self._to_remove_package_set:
            return None

        package_info = None
        if package_id in self._to_install_package_dict:
            package_info = self._to_install_package_dict[package_id]["package_info"]
            package_info["is_installed"] = False
        elif package_id in self._installed_package_dict:
            package_info = self._installed_package_dict[package_id]["package_info"]
            package_info["is_installed"] = True
        elif package_id in self._bundled_package_dict:
            package_info = self._bundled_package_dict[package_id]["package_info"]
            package_info["is_installed"] = True

        if package_info:
            # We also need to get information from the plugin registry such as if a plugin is active
            package_info["is_active"] = self._plugin_registry.isActivePlugin(package_id)
            # If the package ID is in bundled, label it as such
            package_info["is_bundled"] = package_info["package_id"] in self._bundled_package_dict.keys() and not self.isUserInstalledPackage(package_info["package_id"])

        return package_info

    def getAllInstalledPackageIDs(self) -> Set[str]:
        # Add bundled, installed, and to-install packages to the set of installed package IDs
        all_installed_ids = set()  # type: Set[str]

        if self._bundled_package_dict.keys():
            all_installed_ids = all_installed_ids.union(set(self._bundled_package_dict.keys()))
        if self._installed_package_dict.keys():
            all_installed_ids = all_installed_ids.union(set(self._installed_package_dict.keys()))
        all_installed_ids = all_installed_ids.difference(self._to_remove_package_set)
        # If it's going to be installed and to be removed, then the package is being updated and it should be listed.
        if self._to_install_package_dict.keys():
            all_installed_ids = all_installed_ids.union(set(self._to_install_package_dict.keys()))

        return all_installed_ids

    def getAllInstalledPackageIdsAndVersions(self) -> List[Tuple[str, str]]:
        """Get a list of tuples that contain the package ID and version.

        Used by the Marketplace to check which packages have updates available.
        """

        package_ids_and_versions = []  # type: List[Tuple[str, str]]
        all_installed_ids = self.getAllInstalledPackageIDs()
        for package_id in all_installed_ids:
            package_info = self.getInstalledPackageInfo(package_id)
            if package_info is None:
                continue
            if "package_version" not in package_info:
                continue
            package_ids_and_versions.append((package_id, package_info["package_version"]))
        return package_ids_and_versions

    def getAllInstalledPackagesInfo(self) -> Dict[str, List[Dict[str, Any]]]:

        all_installed_ids = self.getAllInstalledPackageIDs()

        # map of <package_type> -> <package_id> -> <package_info>
        installed_packages_dict = {}  # type: Dict[str, List[Dict[str, Any]]]
        for package_id in all_installed_ids:
            # Skip required plugins as they should not be tampered with
            if package_id in self._application.getRequiredPlugins():
                continue

            package_info = self.getInstalledPackageInfo(package_id)

            if package_info is None:
                continue

            # If there is not a section in the dict for this type, add it
            if package_info["package_type"] not in installed_packages_dict:
                installed_packages_dict[package_info["package_type"]] = []

            # Finally, add the data
            installed_packages_dict[package_info["package_type"]].append(package_info)

        return installed_packages_dict

    def getToRemovePackageIDs(self) -> Set[str]:
        return self._to_remove_package_set

    def dismissAllIncompatiblePackages(self, incompatible_packages: List[str]) -> None:
        self._dismissed_packages.update(incompatible_packages)
        self._saveManagementData()
        Logger.debug("Dismissed Incompatible package(s): {}".format(incompatible_packages))

    def getDismissedPackages(self) -> List[str]:
        return list(self._dismissed_packages)

    def reEvaluateDismissedPackages(self, subscribed_packages_payload: List[Dict[str, Any]], sdk_version: str) -> None:
        """
        It removes a package from the "dismissed incompatible packages" list, if
        it gets updated in the meantime. We check every package from the payload
        against our current Cura SDK version, and if it is in there - we remove
        the already dismissed package from the above mentioned list.
        :param subscribed_packages_payload: The response from Web Cura, a list
        of packages that a user is subscribed to.
        :param sdk_version: Current Cura SDK version.
        """
        dismissed_packages = self.getDismissedPackages()
        if dismissed_packages:
            for package in subscribed_packages_payload:
                if package["package_id"] in dismissed_packages and sdk_version in package["sdk_versions"]:
                    self.removeFromDismissedPackages(package["package_id"])

    def removeFromDismissedPackages(self, package: str) -> None:
        if package in self._dismissed_packages:
            self._dismissed_packages.remove(package)
            Logger.debug("Removed package [%s] from the dismissed packages list" % package)

    # Checks if the given package is installed (at all).
    def isPackageInstalled(self, package_id: str) -> bool:
        return self.getInstalledPackageInfo(package_id) is not None

    @pyqtSlot(QUrl)
    def installPackageViaDragAndDrop(self, file_url: str) -> None:
        """This is called by drag-and-dropping curapackage files."""
        filename = QUrl(file_url).toLocalFile()
        return self.installPackage(filename)

    @pyqtSlot(str)
    def installPackage(self, filename: str) -> Optional[str]:
        """Schedules the given package file to be installed upon the next start.

        :return: The to-be-installed package_id or None if something went wrong
        """

        has_changes = False
        package_id = ""
        try:
            # Get package information
            package_info = self.getPackageInfo(filename)
            if not package_info:
                return None
            package_id = package_info["package_id"]

            # If the package is being installed but it is in the list on to remove, then it is deleted from that list.
            if package_id in self._to_remove_package_set:
                self._to_remove_package_set.remove(package_id)

            # We do not check if the same package has been installed already here because, for example, in Cura,
            # it may need to install a package with the same package-version but with a higher SDK version. So,
            # the package-version is not the only version that can be in play here.

            # Need to use the lock file to prevent concurrent I/O issues.
            with self._container_registry.lockFile():
                Logger.log("i", "Package [%s] version [%s] is scheduled to be installed.",
                           package_id, package_info["package_version"])
                # Copy the file to cache dir so we don't need to rely on the original file to be present
                package_cache_dir = os.path.join(os.path.abspath(Resources.getCacheStoragePath()), "cura_packages")
                if not os.path.exists(package_cache_dir):
                    os.makedirs(package_cache_dir, exist_ok=True)

                target_file_path = os.path.join(package_cache_dir, package_id + ".curapackage")
                shutil.copy2(filename, target_file_path)

                self._to_install_package_dict[package_id] = {"package_info": package_info,
                                                             "filename": target_file_path}
                has_changes = True
        except:
            Logger.logException("c", "Failed to install package file '%s'", filename)
        finally:
            self._saveManagementData()
            if has_changes:
                self.installedPackagesChanged.emit()

                if package_id in self._packages_with_update_available:
                    # After installing the update, the check will return that not other updates are available.
                    # In that case we remove it from the list. This is actually a safe check (could be removed)
                    if not self.checkIfPackageCanUpdate(package_id):
                        # The install ensured that the package no longer has a valid update option.
                        self._packages_with_update_available.remove(package_id)
                        self.packagesWithUpdateChanged.emit()

        if has_changes:
            self.packageInstalled.emit(package_id)
            return package_id
        else:
            return None

    # Schedules the given package to be removed upon the next start.
    # \param package_id id of the package
    # \param force_add is used when updating. In that case you actually want to uninstall & install
    @pyqtSlot(str)
    def removePackage(self, package_id: str, force_add: bool = False) -> None:
        # Check the delayed installation and removal lists first
        if not self.isPackageInstalled(package_id):
            Logger.log("i", "Attempt to remove package [%s] that is not installed, do nothing.", package_id)
            return
        # Extra safety check
        if package_id not in self._installed_package_dict and package_id in self._bundled_package_dict:
            Logger.log("i", "Not uninstalling [%s] because it is a bundled package.")
            return

        if package_id not in self._to_install_package_dict or force_add:
            # Schedule for a delayed removal:
            self._to_remove_package_set.add(package_id)
        else:
            if package_id in self._to_install_package_dict:
                # Remove from the delayed installation list if present
                del self._to_install_package_dict[package_id]
        self._saveManagementData()
        self.installedPackagesChanged.emit()

        # It might be that a certain update is suddenly available again!
        if self.checkIfPackageCanUpdate(package_id):
            self._packages_with_update_available.add(package_id)
            self.packagesWithUpdateChanged.emit()

    def isUserInstalledPackage(self, package_id: str) -> bool:
        """Is the package an user installed package?"""

        return package_id in self._installed_package_dict

    # Removes everything associated with the given package ID.
    def _purgePackage(self, package_id: str) -> None:
        # Iterate through all directories in the data storage directory and look for sub-directories that belong to
        # the package we need to remove, that is the sub-dirs with the package_id as names, and remove all those dirs.
        data_storage_dir = os.path.abspath(Resources.getDataStoragePath())

        for root, dir_names, _ in os.walk(data_storage_dir):
            for dir_name in dir_names:
                package_dir = os.path.join(root, dir_name, package_id)
                if os.path.exists(package_dir):
                    Logger.log("i", "Removing '%s' for package [%s]", package_dir, package_id)
                    shutil.rmtree(package_dir)
            break

    # Installs all files associated with the given package.
    def _installPackage(self, installation_package_data: Dict[str, Any]) -> None:
        package_info = installation_package_data["package_info"]
        filename = installation_package_data["filename"]

        package_id = package_info["package_id"]
        Logger.log("i", "Installing package [%s] from file [%s]", package_id, filename)

        # Load the cached package file and extract all contents to a temporary directory
        if not os.path.exists(filename):
            Logger.log("w", "Package [%s] file '%s' is missing, cannot install this package", package_id, filename)
            return
        try:
            with zipfile.ZipFile(filename, "r") as archive:
                temp_dir = tempfile.TemporaryDirectory()
                archive.extractall(temp_dir.name)
        except Exception:
            Logger.logException("e", "Failed to install package from file [%s]", filename)
            return

        # Remove it first and then install
        try:
            self._purgePackage(package_id)
        except Exception as e:
            message = Message(catalog.i18nc("@error:update",
                                            "There was an error uninstalling the package {package} before installing "
                                            "new version:\n{error}.\nPlease try to upgrade again later.".format(
                                            package = package_id, error = str(e))),
                              title = catalog.i18nc("@info:title", "Updating error"))
            message.show()
            return

        # Copy the folders there
        for sub_dir_name, installation_root_dir in self._installation_dirs_dict.items():
            src_dir_path = os.path.join(temp_dir.name, "files", sub_dir_name)
            dst_dir_path = os.path.join(installation_root_dir, package_id)

            if not os.path.exists(src_dir_path):
                Logger.log("w", "The path %s does not exist, so not installing the files", src_dir_path)
                continue
            try:
                self.__installPackageFiles(package_id, src_dir_path, dst_dir_path)
            except EnvironmentError as e:
                Logger.log("e", "Can't install package due to EnvironmentError: {err}".format(err = str(e)))
                continue

        # Remove the file
        try:
            os.remove(filename)
        except Exception:
            Logger.log("w", "Tried to delete file [%s], but it failed", filename)

        # Move the info to the installed list of packages only when it succeeds
        self._installed_package_dict[package_id] = self._to_install_package_dict[package_id]
        self._installed_package_dict[package_id]["package_info"]["is_installed"] = True

    def __installPackageFiles(self, package_id: str, src_dir: str, dst_dir: str) -> None:
        Logger.log("i", "Moving package {package_id} from {src_dir} to {dst_dir}".format(package_id=package_id, src_dir=src_dir, dst_dir=dst_dir))
        try:
            shutil.move(src_dir, dst_dir)
        except FileExistsError:
            Logger.log("w", "Not moving %s to %s as the destination already exists", src_dir, dst_dir)
        except EnvironmentError as e:
            Logger.log("e", "Can't install package, operating system is blocking it: {err}".format(err = str(e)))

    # Gets package information from the given file.
    def getPackageInfo(self, filename: str) -> Dict[str, Any]:
        package_json = {}  # type: Dict[str, Any]
        try:
            with zipfile.ZipFile(filename) as archive:
                # Go through all the files and use the first successful read as the result
                for file_info in archive.infolist():
                    if file_info.filename.endswith("package.json"):
                        Logger.log("d", "Found potential package.json file '%s'", file_info.filename)
                        try:
                            with archive.open(file_info.filename, "r") as f:
                                package_json = json.loads(f.read().decode("utf-8"))

                            # Add by default properties
                            package_json["is_active"] = True
                            package_json["is_bundled"] = False
                            package_json["is_installed"] = False
                            break
                        except:
                            Logger.logException("e", "Failed to load potential package.json file '%s' as text file.",
                                                file_info.filename)
        except (zipfile.BadZipFile, LookupError):  # Corrupt zip file, or unknown encoding.
            Logger.logException("e", "Failed to unpack the file %s", filename)
        return package_json

    # Gets the license file content if present in the given package file.
    # Returns None if there is no license file found.
    def getPackageLicense(self, filename: str) -> Optional[str]:
        license_string = None
        def is_license(zipinfo: zipfile.ZipInfo) -> bool:
            return os.path.basename(zipinfo.filename).startswith("LICENSE")
        try:
            with zipfile.ZipFile(filename) as archive:
                # Go through all the files and use the first successful read as the result
                license_files = sorted(filter(is_license, archive.infolist()), key = lambda x: len(x.filename))  # Find the one with the shortest path.
                for file_info in license_files:
                    Logger.log("d", "Found potential license file '{filename}'".format(filename = file_info.filename))
                    try:
                        with archive.open(file_info.filename, "r") as f:
                            data = f.read()
                        license_string = data.decode("utf-8")
                        break
                    except:
                        Logger.logException("e", "Failed to load potential license file '%s' as text file.", file_info.filename)
                        license_string = None
        except zipfile.BadZipFile as e:
            Logger.error("Package is corrupt: {err}".format(err = str(e)))
            license_string = None
        except UnicodeDecodeError:
            Logger.error("Package filenames are not UTF-8 encoded! Encoding unknown.")
            license_string = None
        return license_string

    @staticmethod
    def getPackageFiles(package_id) -> List[Tuple[str, List[str]]]:
        """Find the package files by package_id by looking at the installed folder"""

        data_storage_dir = os.path.abspath(Resources.getDataStoragePath())

        os_walk = []
        dirs_to_check = []
        result = []  # 2-tuples of (dir, file_names)
        for root_path, dir_names, file_names in os.walk(data_storage_dir):
            os_walk.append((root_path, dir_names, file_names))
            for dir_name in dir_names:
                package_dir = os.path.join(root_path, dir_name, package_id)
                if os.path.exists(package_dir):
                    dirs_to_check.append(package_dir)

        for root_path, dir_names, file_names in os_walk:
            for dir_to_check in dirs_to_check:
                if root_path.startswith(dir_to_check):
                    result.append((root_path, file_names))

        return result

    @staticmethod
    def getPackageContainerIds(package_id: str) -> List[str]:
        """Return container ids for contents found with package_id"""

        package_files = PackageManager.getPackageFiles(package_id)
        ids = []
        for root_path, file_names in package_files:
            for file_name in file_names:
                path = os.path.join(root_path, file_name)
                id = PackageManager.convertPathToId(path)
                if id:
                    ids.append(id)
        return ids

    @staticmethod
    def convertPathToId(path: str) -> str:
        """Try to return Id for given path by looking at its existence in the mimetype database"""

        mime = None
        try:
            mime = MimeTypeDatabase.getMimeTypeForFile(path)
        except MimeTypeDatabase.MimeTypeNotFoundError:
            pass
        if mime:
            return urllib.parse.unquote_plus(mime.stripExtension(os.path.basename(path)))
        else:
            return ""


__all__ = ["PackageManager"]
