# Copyright (c) 2022 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.
import platform
import json
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Type

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtNetwork import QNetworkRequest

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Message import Message
from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.Version import Version
from UM.i18n import i18nCatalog
from .NewBetaVersionMessage import NewBetaVersionMessage
from .NewVersionMessage import NewVersionMessage

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkReply


i18n_catalog = i18nCatalog("uranium")


class UpdateChecker(Extension):
    """This Extension checks for new versions of the application based on the application name and the version number.

    The plugin is currently only usable for applications maintained by Ultimaker. But it should be relatively easy
    to change it to work for other applications.
    """
    url = "https://software.ultimaker.com/latest.json"

    def __init__(self) -> None:
        super().__init__()
        self.setMenuName(i18n_catalog.i18nc("@item:inmenu", "Update Checker"))
        self.addMenuItem(i18n_catalog.i18nc("@item:inmenu", "Check for Updates"), self.checkNewVersion)
        preferences = Application.getInstance().getPreferences()
        preferences.addPreference("info/automatic_update_check", True)
        if preferences.getValue("info/automatic_update_check"):
            self.checkNewVersion(silent = True, display_same_version = False)

        self._download_url: Optional[str] = None

        # Which version was the latest shown in the version upgrade dialog. Don't show these updates twice.
        preferences.addPreference("info/latest_update_version_shown", Application.getInstance().getVersion())
        preferences.addPreference("info/latest_beta_update_version_shown", Application.getInstance().getVersion())

        preferences.addPreference("info/latest_update_source", "beta")

    def checkNewVersion(self, silent = False, display_same_version = True) -> None:
        """Connect with software.ultimaker.com, load latest.json and check version info.

        If the version info is higher then the current version, spawn a message to
        allow the user to download it.

        :param silent: Suppresses messages other than "new version found"
        messages. This is used when checking for a new version at startup.
        :param display_same_version: Whether to display the same update message
        twice (True) or suppress the update message if the user has already seen
        the update for a particular version. When manually checking for updates,
        the user wants to display the update even if he's already seen it.
        """
        http_manager = HttpRequestManager.getInstance()
        Logger.log("i", "Checking for new version")
        http_manager.get(self.url, callback = lambda reply: self._onRequestCompleted(reply, silent, display_same_version))
        self._download_url = None

    @classmethod
    def _extractVersionAndURLFromData(cls, data: Dict, application_name: str) -> Tuple[Optional[Version], Optional[str]]:
        if application_name not in data:
            return None, None

        os = platform.system()
        if os not in data[application_name]:
            return None, None

        return Version([int(data[application_name][os]["major"]),
                        int(data[application_name][os]["minor"]),
                        int(data[application_name][os]["revision"])]), data[application_name][os]["url"]

    def _onRequestCompleted(self, reply: "QNetworkReply", silent: bool, display_same_version: bool) -> None:
        if reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) != 200:
            Logger.log("w", "Something went wrong when checking for updates. We didn't get the expected response")
            return
        try:
            data = json.loads(bytes(reply.readAll()).decode())
        except Exception:
            Logger.logException("w", "Failed to parse update data")
            return

        app_version = Application.getInstance().getVersion()
        # Skip if we're on a dev version
        if app_version == "master" or app_version == Version([0, 0, 0]):
            if not silent:
                Message(i18n_catalog.i18nc("@info", "The version you are using does not support checking for updates."),
                        title=i18n_catalog.i18nc("@info:title", "Warning")).show()
            return
        application_name = Application.getInstance().getApplicationName()
        newest_version, download_url = self._extractVersionAndURLFromData(data, application_name)
        newest_beta_version, beta_download_url = self._extractVersionAndURLFromData(data, application_name + "-beta")

        if newest_version is None:
            Logger.log("w", "Unable to extract latest version from the provided data.")
            newest_version = Version("0.0.0")

        if newest_beta_version is None:
            Logger.log("w", "Unable to extract BETA version from the provided data.")
            newest_beta_version = Version("0.0.0")

        if download_url is not None:
            self._download_url = download_url

        local_version = Version(app_version)
        preferences = Application.getInstance().getPreferences()
        if preferences.getValue("info/latest_update_source") == "beta":
            if newest_version >= newest_beta_version:
                # The stable release is higher than the beta, check if we need to show that!
                self._handleLatestUpdate(local_version, newest_version, silent, display_same_version, NewVersionMessage,
                                         "info/latest_update_version_shown")
            else:
                # Beta version is the highest, check for that
                local_version = local_version.getWithoutPostfix()  # Since we can't specify postfix in the latest.json.
                if download_url is not None:
                    self._download_url = beta_download_url
                self._handleLatestUpdate(local_version, newest_beta_version, silent, display_same_version,
                                         NewBetaVersionMessage, "info/latest_beta_update_version_shown")
        else:
            # Only handle stable release!
            self._handleLatestUpdate(local_version, newest_version, silent, display_same_version, NewVersionMessage,
                                     "info/latest_update_version_shown")

    def _handleLatestUpdate(self, local_version: Version, newest_version: Version, silent: bool, display_same_version: bool, message_class: Type, preference_key: str) -> bool:
        """

        :param local_version: Local version of the application
        :param newest_version: Newest version (as reported by remote)
        :param silent: Should any other message but "a new update is there" be supressed?
        :param display_same_version: Should a message be shown if there is no new version?
        :param message_class: What message class should be used to spawn the message if a new version was found
        :param preference_key: What preference key should be used to check (and set) the latest shown version?
        :return: True if an action was taken, false otherwise
        """

        preferences = Application.getInstance().getPreferences()
        latest_version_shown = preferences.getValue(preference_key)

        if local_version == newest_version:
            if local_version > latest_version_shown:
                preferences.setValue(preference_key, str(local_version))
            if display_same_version and not silent:
                Message(i18n_catalog.i18nc("@info", "No new version was found."),
                        title=i18n_catalog.i18nc("@info:title", "Version Upgrade")).show()
                return True
            return False  # Nothing to do!

        if local_version < latest_version_shown and not display_same_version:
            return False  # User was already informed once.

        if local_version > newest_version:
            return False  # No idea how this can happen, but don't bother the user with this.

        preferences.setValue(preference_key, str(newest_version))
        Logger.log("i", "Found a new version of the software. Spawning message")

        message = message_class(
            application_display_name = Application.getInstance().getApplicationDisplayName().title(),
            newest_version = newest_version)
        message.download_url = self._download_url  # At this point 'our own' _download_url is set to the correct value.
        message.actionTriggered.connect(self._onActionTriggered)
        message.show()
        return True

    def _onActionTriggered(self, message: Message, action: str) -> None:
        """Callback function for the "download" button on the update notification.

        This function is here is because the custom Signal in Uranium keeps a list of weak references to its
        connections, so the callback functions need to be long-lived.
        """
        if action == "download":
            if self._download_url is not None:
                QDesktopServices.openUrl(QUrl(message.download_url))
        elif action == "new_features":
            QDesktopServices.openUrl(QUrl(message.change_log_url))
