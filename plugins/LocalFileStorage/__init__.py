from . import LocalFileStorageDevice

def getMetaData():
    return { "name": "Local File Storage", "type": "StorageDevice" }

def register(app):
    device = LocalFileStorageDevice.LocalFileStorageDevice()
    app.addStorageDevice("local", device)

