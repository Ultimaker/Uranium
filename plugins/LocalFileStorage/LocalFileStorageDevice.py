from Cura.StorageDevice import StorageDevice

class LocalFileStorageDevice(StorageDevice):
    def __init__(self):
        super(LocalFileStorageDevice, self).__init__()

    def openFile(self, file_name, mode):
        return open(file_name, mode)