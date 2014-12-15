from plugins.ScannerEngineBackend import ScannerEngineBackend

def getMetaData():
    return { "name": "ScannerBackend", "type": "Backend" }

def register(app):
    engine = ScannerEngineBackend.ScannerEngineBackend()
    app.setBackend(engine)