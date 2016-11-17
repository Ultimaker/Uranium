# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Extension import Extension
from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Application import Application
from UM.Message import Message
from UM.Version import Version
from UM.Preferences import Preferences
from UM.Job import Job

import urllib.request
import platform
import json
import codecs
import webbrowser

i18n_catalog = i18nCatalog("uranium")

class UpdateCheckerJob(Job):
    def __init__(self, silent = False, url = None):
        super().__init__()
        self.silent = silent
        self.url = url

    ##  Callback for the message that is spawned when there is a new version.
    def actionTriggered(self, message, action):
        if action == "download":
            if self._url is not None:
                webbrowser.open(self._url)

    def run(self):
        if not self.url:
            Logger.log("e", "Can not check for a new release. URL not set!")
        no_new_version = True

        application_name = Application.getInstance().getApplicationName()
        Logger.log("i", "Checking for new version of %s" % application_name)

        try:
            latest_version_file = urllib.request.urlopen(self.url)
        except Exception as e:
            Logger.log("w", "Failed to check for new version: %s" % e)
            if not self.silent:
                Message(i18n_catalog.i18nc("@info", "Could not access update information.")).show()
            return

        try:
            reader = codecs.getreader("utf-8")
            data = json.load(reader(latest_version_file))
            try:
                if Application.getInstance().getVersion() is not "master":
                    local_version = Version(Application.getInstance().getVersion())
                else:
                    if not self.silent:
                        Message(i18n_catalog.i18nc("@info", "The version you are using does not support checking for updates.")).show()
                    return
            except ValueError:
                Logger.log("w", "Could not determine application version from string %s, not checking for updates", Application.getInstance().getVersion())
                if not self.silent:
                    Message(i18n_catalog.i18nc("@info", "The version you are using does not support checking for updates.")).show()
                return

            if application_name in data:
                for key, value in data[application_name].items():
                    if "major" in value and "minor" in value and "revision" in value and "url" in value:
                        os = key
                        if platform.system() == os: #TODO: add architecture check
                            newest_version = Version([int(value["major"]), int(value["minor"]), int(value["revision"])])
                            if local_version < newest_version:
                                Logger.log("i", "Found a new version of the software. Spawning message")
                                message = Message(i18n_catalog.i18nc("@info", "A new version is available!"))
                                message.addAction("download", i18n_catalog.i18nc("@action:button", "Download"), "[no_icon]", "[no_description]")
                                self._url = value["url"]
                                message.actionTriggered.connect(self.actionTriggered)
                                message.show()
                                no_new_version = False
                                break
                    else:
                        Logger.log("w", "Could not find version information or download url for update.")
            else:
                Logger.log("w", "Did not find any version information for %s." % application_name)
        except Exception:
            Logger.logException("e", "Exception in update checker while parsing the JSON file.")
            Message(i18n_catalog.i18nc("@info", "An exception occured while parsing the JSON file.")).show()
            no_new_version = False # Just to suppress the message below.

        if no_new_version and not self.silent:
            Message(i18n_catalog.i18nc("@info", "No new version was found.")).show()


## This extention checks for new versions of the application based on the application name and the version number.
#  The plugin is currently only usuable for applications maintained by Ultimaker. But it should be relatively easy
#  to change it to work for other applications.
class UpdateChecker(Extension):
    url = "http://software.ultimaker.com/latest.json"

    def __init__(self):
        super().__init__()
        self.addMenuItem(i18n_catalog.i18nc("@item:inmenu", "Check for Updates"), self.checkNewVersion)

        Preferences.getInstance().addPreference("info/automatic_update_check", True)
        if Preferences.getInstance().getValue("info/automatic_update_check"):
            self.checkNewVersion(True)

    ##  Connect with software.ultimaker.com, load latest.json and check version info.
    #   If the version info is higher then the current version, spawn a message to
    #   allow the user to download it.
    #
    #   \param silent type(boolean) Suppresses messages other than "new version found" messages.
    #                               This is used when checking for a new version at startup.
    def checkNewVersion(self, silent = False):
        job = UpdateCheckerJob(silent = silent, url = self.url)
        job.start()