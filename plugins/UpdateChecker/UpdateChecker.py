from UM.Extension import Extension
from UM.Logger import Logger
from UM.i18n import i18nCatalog
import urllib.request
import platform
from UM.Application import Application
import json
import codecs
import webbrowser
from threading import Thread
from UM.Message import Message
        
i18n_catalog = i18nCatalog('plugins')


class UpdateChecker(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem(i18n_catalog.i18n("Check new version"), self.checkNewVersion)
        self._url = None
        thread = Thread(target=self.checkNewVersion)
        thread.daemon = True
        thread.start()

    def actionTriggered(self, action):
        if action == "Download":
            if self._url is not None: 
                webbrowser.open(self._url)
 
    def checkNewVersion(self):
        Logger.log('i', "Checking new version")
        
        try:
            latest_version_file = urllib.request.urlopen("http://software.ultimaker.com/latest.json")
        except:
            Logger.log('e', "Failed to check for new version")
        
        try:
            reader = codecs.getreader("utf-8")
            data = json.load(reader(latest_version_file))
            application_name = Application.getInstance().getApplicationName()
            local_version = list(map(int, Application.getInstance().getVersion().split('.')))
            if application_name in data:
                for key, value in data[application_name].items():
                    if "major" in value and "minor" in value and "revision" in value and "url" in value:
                        os = key
                        if platform.system() == os: #TODO: add architecture check
                            newest_version = [int(value["major"]), int(value['minor']), int(value['revision'])]
                            if local_version < newest_version:
                                message = Message(i18n_catalog.i18n("A new version is available!"))
                                message.addAction("Download", "[no_icon]", "[no_description]")
                                self._url = value["url"]
                                message.actionTriggered.connect(self.actionTriggered)
                                message.show()

        except Exception as e:
            Logger.log('e', "Exception in update checker: %s" % (e))
