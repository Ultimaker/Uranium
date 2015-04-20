from UM.Extension import Extension
from UM.i18n import i18nCatalog
import urllib.request
import platform
from UM.Application import Application
import json
import codecs
import webbrowser
        
i18n_catalog = i18nCatalog('plugins')

class UpdateChecker(Extension):
    def __init__(self):
        super().__init__()
        self.addMenuItem(i18n_catalog.i18n("Check new version"), self.checkNewVersion)
        self.checkNewVersion()
        
        
    def checkNewVersion(self):
        print("Checking new version")
        
        try:
            file_name = "UpdateCheckTest.json"
            latest_version_file = urllib.request.urlopen("http://software.ultimaker.com/latest.json")
        except:
            print("Failed to check for new version")
        
        #
        try:
            reader = codecs.getreader("utf-8")
            data = json.load(reader(latest_version_file))
            application_name = Application.getInstance().getApplicationName()
            local_version = list(map(int,Application.getInstance().getVersion().split('.')))
            if application_name in data:
                for key, value in data[application_name].items():
                    if "major" in value and "minor" in value and "revision" in value and "url" in value:
                        os = str(key)
                        if platform.system() == os: #TODO: add architecture check
                            newest_version= [int(value["major"]), int(value['minor']), int(value['revision'])]
                            if local_version < newest_version:
                                #TODO: open dialog
                                pass
                                #webbrowser.open(value["url"])
                            
        except Exception as e:
            print("error yay! %s" %e)
            pass