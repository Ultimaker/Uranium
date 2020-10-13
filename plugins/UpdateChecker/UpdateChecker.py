# Copyright (c) 2018 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from UM.Application import Application
from UM.Extension import Extension
from UM.i18n import i18nCatalog
from .UpdateCheckerJob import UpdateCheckerJob

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
        self._download_url = None
        job = UpdateCheckerJob(silent, display_same_version, self.url, self._onActionTriggered, self._onSetDownloadUrl)
        job.start()

    def _onSetDownloadUrl(self, download_url):
        self._download_url = download_url

    def _onActionTriggered(self, message, action):
        """Callback function for the "download" button on the update notification.

        This function is here is because the custom Signal in Uranium keeps a list of weak references to its
        connections, so the callback functions need to be long-lived. The UpdateCheckerJob is short-lived so
        this function cannot be there.
        """
        if action == "download":
            if self._download_url is not None:
                QDesktopServices.openUrl(QUrl(self._download_url))
        elif action == "new_features":
            QDesktopServices.openUrl(QUrl(Application.getInstance().change_log_url))
