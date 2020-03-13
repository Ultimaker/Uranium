# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import codecs
import json
import platform
import ssl
import urllib.request

import certifi

from UM.Application import Application
from UM.Job import Job
from UM.Logger import Logger
from UM.Message import Message
from UM.Version import Version
from UM.i18n import i18nCatalog

i18n_catalog = i18nCatalog("uranium")


class UpdateCheckerJob(Job):
    """This job checks if there is an update available on the provided URL."""

    def __init__(self, silent = False, display_same_version = True, url = None, callback = None, set_download_url_callback = None):
        super().__init__()
        self.silent = silent
        self.display_same_version = display_same_version
        self._url = url
        self._callback = callback
        self._set_download_url_callback = set_download_url_callback

    def run(self):
        if not self._url:
            Logger.log("e", "Can not check for a new release. URL not set!")
        no_new_version = True

        application_name = Application.getInstance().getApplicationName()

        Logger.log("i", "Checking for new version of %s" % application_name)
        try:
            headers = {"User-Agent": "%s - %s" % (application_name, Application.getInstance().getVersion())}
            # CURA-6698 Create an SSL context and use certifi CA certificates for verification.
            context = ssl.SSLContext(protocol = ssl.PROTOCOL_TLSv1_2)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(cafile = certifi.where())
            request = urllib.request.Request(self._url, headers = headers)
            latest_version_file = urllib.request.urlopen(request, context = context)
        except Exception as e:
            Logger.logException("w", "Failed to check for new version: %s" % e)
            if not self.silent:
                Message(i18n_catalog.i18nc("@info", "Could not access update information."),
                    title = i18n_catalog.i18nc("@info:title", "Version Upgrade")
                ).show()
            return

        try:
            reader = codecs.getreader("utf-8")
            data = json.load(reader(latest_version_file))
            try:
                if Application.getInstance().getVersion() != "master":
                    local_version = Version(Application.getInstance().getVersion())
                else:
                    if not self.silent:
                        Message(i18n_catalog.i18nc("@info", "The version you are using does not support checking for updates."), title = i18n_catalog.i18nc("@info:title", "Warning")).show()
                    return
            except ValueError:
                Logger.log("w", "Could not determine application version from string %s, not checking for updates", Application.getInstance().getVersion())
                if not self.silent:
                    Message(i18n_catalog.i18nc("@info", "The version you are using does not support checking for updates."), title = i18n_catalog.i18nc("@info:title", "Version Upgrade")).show()
                return

            if application_name in data:
                for key, value in data[application_name].items():
                    if "major" in value and "minor" in value and "revision" in value and "url" in value:
                        os = key
                        if platform.system() == os: #TODO: add architecture check
                            newest_version = Version([int(value["major"]), int(value["minor"]), int(value["revision"])])
                            if local_version < newest_version:
                                preferences = Application.getInstance().getPreferences()
                                latest_version_shown = preferences.getValue("info/latest_update_version_shown")
                                if latest_version_shown == newest_version and not self.display_same_version:
                                    continue  # Don't show this update again. The user already clicked it away and doesn't want it again.
                                preferences.setValue("info/latest_update_version_shown", str(newest_version))
                                Logger.log("i", "Found a new version of the software. Spawning message")
                                self.showUpdate(newest_version, value["url"])
                                no_new_version = False
                                break
                    else:
                        Logger.log("w", "Could not find version information or download url for update.")
            else:
                Logger.log("w", "Did not find any version information for %s." % application_name)
        except Exception:
            Logger.logException("e", "Exception in update checker while parsing the JSON file.")
            Message(i18n_catalog.i18nc("@info", "An error occurred while checking for updates."), title = i18n_catalog.i18nc("@info:title", "Error")).show()
            no_new_version = False  # Just to suppress the message below.

        if no_new_version and not self.silent:
            Message(i18n_catalog.i18nc("@info", "No new version was found."), title = i18n_catalog.i18nc("@info:title", "Version Upgrade")).show()

    def showUpdate(self, newest_version: Version, download_url: str) -> None:
        application_display_name = Application.getInstance().getApplicationDisplayName().title()
        title_message = i18n_catalog.i18nc("@info:status",
                                           "{application_name} {version_number} is available!".format(application_name = application_display_name, version_number = newest_version))
        content_message = i18n_catalog.i18nc("@info:status",
                                             "{application_name} {version_number} provides a better and more reliable printing experience.".format(application_name = application_display_name, version_number = newest_version))

        message = Message(text = content_message, title = title_message)
        message.addAction("download", i18n_catalog.i18nc("@action:button", "Download"), "[no_icon]", "[no_description]")

        message.addAction("new_features", i18n_catalog.i18nc("@action:button", "Learn more"), "[no_icon]", "[no_description]",
                          button_style = Message.ActionButtonStyle.LINK,
                          button_align = Message.ActionButtonAlignment.ALIGN_LEFT)

        if self._set_download_url_callback:
            self._set_download_url_callback(download_url)
        message.actionTriggered.connect(self._callback)
        message.show()