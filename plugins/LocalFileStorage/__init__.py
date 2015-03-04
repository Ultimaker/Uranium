from . import LocalFileStorageDevice

def getMetaData():
    return {
        'type': 'storage_device',
        'plugin': {
            'name': 'Local File Storage',
            'author': 'Arjen Hiemstra',
            'version': '1.0',
            'description': 'Provides access to local files.'
        }
    }

def register(app):
    return LocalFileStorageDevice.LocalFileStorageDevice()

