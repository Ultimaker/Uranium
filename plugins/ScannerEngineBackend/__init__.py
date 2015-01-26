from plugins.ScannerEngineBackend import ScannerEngineBackend
from UM.Preferences import Preferences
from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType
from . import ScannerEngineBackendProxy

def getMetaData():
    return { "name": "ScannerBackend", "type": "Backend", "author":"Jaime van Kessel", "about": "Its. So. Awesome","version": "1.0" }

def createScannerEngineBackendProxy(engine, scriptEngine):
    return ScannerEngineBackendProxy.ScannerEngineBackendProxy()

def register(app):
    Preferences.addPreference("BackendLocation","../UltiScanTastic/Scanner/bin/Debug/Ultiscantastic")
    engine = ScannerEngineBackend.ScannerEngineBackend()
    app.setBackend(engine)
    qmlRegisterSingletonType(ScannerEngineBackendProxy.ScannerEngineBackendProxy, "UM", 1, 0, "ScannerEngineBackend", createScannerEngineBackendProxy)
    
    
   
