from LocalFileStorageDevice import LocalFileStorageDevice

def getMetaData():
    return { "name": "Local File Storage", "type": "StorageDevice" }

def register(app):
    device = LocalFileStorageDevice()
    app.addStorageDevice("local", device)

