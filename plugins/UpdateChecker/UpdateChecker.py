# Copyright (c) 2017 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Extension import Extension
from UM.i18n import i18nCatalog

from UM.Preferences import Preferences

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from .UpdateCheckerJob import UpdateCheckerJob

i18n_catalog = i18nCatalog("uranium")


## This Extension checks for new versions of the application based on the application name and the version number.
#  The plugin is currently only usable for applications maintained by Ultimaker. But it should be relatively easy
#  to change it to work for other applications.
class UpdateChecker(Extension):
    url = "http://software.ultimaker.com/latest.json"

    def __init__(self):
        super().__init__()
        self.addMenuItem(i18n_catalog.i18nc("@item:inmenu", "Check for Updates"), self.checkNewVersion)

        Preferences.getInstance().addPreference("info/automatic_update_check", True)
        if Preferences.getInstance().getValue("info/automatic_update_check"):
            self.checkNewVersion(True)

        self._download_url = None

    ##  Connect with software.ultimaker.com, load latest.json and check version info.
    #   If the version info is higher then the current version, spawn a message to
    #   allow the user to download it.
    #
    #   \param silent type(boolean) Suppresses messages other than "new version found" messages.
    #                               This is used when checking for a new version at startup.
    def checkNewVersion(self, silent = False):
        self._download_url = None
        job = UpdateCheckerJob(silent, self.url, self._onActionTriggered, self._onSetDownloadUrl)
        job.start()

    def _onSetDownloadUrl(self, download_url):
        self._download_url = download_url

    ##  Callback function for the "download" button on the update notification.
    #   This function is here is because the custom Signal in Uranium keeps a list of weak references to its
    #   connections, so the callback functions need to be long-lived. The UpdateCheckerJob is short-lived so
    #   this function cannot be there.
    def _onActionTriggered(self, message, action):
        if action == "download":
            if self._download_url is not None:
                QDesktopServices.openUrl(QUrl(self._download_url))
        elif action == "new_features":
            QDesktopServices.openUrl(QUrl("https://ultimaker.com/ultimaker-cura-latest-features"))
