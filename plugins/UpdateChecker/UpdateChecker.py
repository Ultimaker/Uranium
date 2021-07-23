# Copyright (c) 2021 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.
import platform
import json

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtNetwork import QNetworkRequest

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Message import Message
from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.Version import Version
from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog("uranium")


class UpdateChecker(Extension):
    """This Extension checks for new versions of the application based on the application name and the version number.

    The plugin is currently only usable for applications maintained by Ultimaker. But it should be relatively easy
    to change it to work for other applications.
    """
    url = "https://software.ultimaker.com/latest.json"

    def __init__(self):
        super().__init__()
        self.setMenuName(i18n_catalog.i18nc("@item:inmenu", "Update Checker"))
        self.addMenuItem(i18n_catalog.i18nc("@item:inmenu", "Check for Updates"), self.checkNewVersion)

        Application.getInstance().getPreferences().addPreference("info/automatic_update_check", True)
        if Application.getInstance().getPreferences().getValue("info/automatic_update_check"):
            self.checkNewVersion(silent = True, display_same_version = False)

        self._download_url = None

        # Which version was the latest shown in the version upgrade dialog. Don't show these updates twice.
        Application.getInstance().getPreferences().addPreference("info/latest_update_version_shown", "0.0.0")

    def checkNewVersion(self, silent = False, display_same_version = True):
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

    def _onRequestCompleted(self, reply, silent, display_same_version):
        if reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) != 200:
            # TODO: Show failure message
            return
        try:
            data = json.loads(bytes(reply.readAll()).decode())
        except Exception:
            Logger.logException("w", "Failed to parse update data")
            # Todo more explicit exception handling & showing of error messages
            return

        application_name = Application.getInstance().getApplicationName()
        if application_name not in data:
            #TODO: Warn user about this
            return

        cura_data = data[application_name]
        os = platform.system()
        if os not in cura_data:
            # TODO: warn user
            return

        app_version = Application.getInstance().getVersion()
        # Skip if we're on a dev version
        if app_version == "master" or app_version == Version([0, 0, 0]):
            if not silent:
                Message(i18n_catalog.i18nc("@info", "The version you are using does not support checking for updates."),
                        title=i18n_catalog.i18nc("@info:title", "Warning")).show()
            return

        local_version = Version(Application.getInstance().getVersion())
        newest_version = Version([int(cura_data[os]["major"]), int(cura_data[os]["minor"]), int(cura_data[os]["revision"])])

        preferences = Application.getInstance().getPreferences()
        latest_version_shown = preferences.getValue("info/latest_update_version_shown")

        if local_version == newest_version and local_version == latest_version_shown:
            if display_same_version and not silent:
                Message(i18n_catalog.i18nc("@info", "No new version was found."),
                        title=i18n_catalog.i18nc("@info:title", "Version Upgrade")).show()
            return  # Nothing to do!

        if local_version < latest_version_shown and not display_same_version:
            return  # User was already informed once.

        if local_version > newest_version:
            return  # No idea how this can happen, but don't bother the user with this.
        self._download_url = cura_data[os]["url"]
        preferences.setValue("info/latest_update_version_shown", str(newest_version))
        Logger.log("i", "Found a new version of the software. Spawning message")

        application_display_name = Application.getInstance().getApplicationDisplayName().title()
        title_message = i18n_catalog.i18nc("@info:status",
                                           "{application_name} {version_number} is available!".format(
                                               application_name=application_display_name,
                                               version_number=newest_version))
        content_message = i18n_catalog.i18nc("@info:status",
                                             "{application_name} {version_number} provides a better and more reliable printing experience.".format(
                                                 application_name=application_display_name,
                                                 version_number=newest_version))

        message = Message(text=content_message, title=title_message)
        message.addAction("download", i18n_catalog.i18nc("@action:button", "Download"), "[no_icon]", "[no_description]")

        message.addAction("new_features", i18n_catalog.i18nc("@action:button", "Learn more"), "[no_icon]",
                          "[no_description]",
                          button_style=Message.ActionButtonStyle.LINK,
                          button_align=Message.ActionButtonAlignment.ALIGN_LEFT)

        message.actionTriggered.connect(self._onActionTriggered)
        message.show()

    def _onActionTriggered(self, message, action):
        """Callback function for the "download" button on the update notification.

        This function is here is because the custom Signal in Uranium keeps a list of weak references to its
        connections, so the callback functions need to be long-lived.
        """
        if action == "download":
            if self._download_url is not None:
                QDesktopServices.openUrl(QUrl(self._download_url))
        elif action == "new_features":
            QDesktopServices.openUrl(QUrl(Application.getInstance().change_log_url))
