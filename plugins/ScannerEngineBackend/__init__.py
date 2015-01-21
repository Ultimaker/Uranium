from plugins.ScannerEngineBackend import ScannerEngineBackend
from UM.Preferences import Preferences

def getMetaData():
    return { "name": "ScannerBackend", "type": "Backend", "author":"Jaime van Kessel", "about": "Its. So. Awesome","version": "1.0" }

def register(app):
    Preferences.addPreference("BackendLocation","../UltiScanTastic/Scanner/bin/Debug/Ultiscantastic")
    engine = ScannerEngineBackend.ScannerEngineBackend()
    app.setBackend(engine)