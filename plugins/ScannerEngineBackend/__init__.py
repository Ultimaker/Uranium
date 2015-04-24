from plugins.ScannerEngineBackend import ScannerEngineBackend
from UM.Preferences import Preferences
from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType
from . import ScannerEngineBackendProxy


def getMetaData():
    return {
        'type': 'backend',
        'plugin': {
            "name": "ScannerBackend",
            "author":"Jaime van Kessel",
            "description": "Its. So. Awesome",
            "version": "1.0"
        }
    }

def createScannerEngineBackendProxy(engine, scriptEngine):
    return ScannerEngineBackendProxy.ScannerEngineBackendProxy()

def createCameraImageProvider(engine, scriptEngine):
    return CameraImageProvider.CameraImageProvider()

def register(app):
    qmlRegisterSingletonType(ScannerEngineBackendProxy.ScannerEngineBackendProxy, "UM", 1, 0, "ScannerEngineBackend", createScannerEngineBackendProxy)
    return {"backend":ScannerEngineBackend.ScannerEngineBackend()}

    #addImageProvider("test",image_provider)
    
   
