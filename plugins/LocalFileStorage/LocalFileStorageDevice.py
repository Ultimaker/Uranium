from UM.StorageDevice import StorageDevice

import platform
import os

class LocalFileStorageDevice(StorageDevice):
    def __init__(self):
        super(LocalFileStorageDevice, self).__init__()
        self._drives = []
        self._removableDrives = self._createRemovableDrives()

    def openFile(self, file_name, mode):
        return open(file_name, mode)

    def closeFile(self, file):
        file.close()

    def ejectRemovableDrive(self, name):
        if self._removableDrives:
            self._removableDrives.ejectDrive(name)

    def hasRemovableDrives(self):
        if self._removableDrives:
            return self._removableDrives.hasDrives()

    def getRemovableDrives(self):
        if self._removableDrives:
            return self._removableDrives.getDrives()

    def _createRemovableDrives(self):
        if platform.system() == "Windows":
            from . import WindowsRemovableDrives
            return WindowsRemovableDrives.WindowsRemovableDrives()
        elif platform.system() == "Darwin":
            from . import OSXRemovableDrives
            return OSXRemovableDrives.OSXRemovableDrives()
        elif platform.system() == "Linux":
            from . import LinuxRemovableDrives
            return LinuxRemovableDrives.LinuxRemovableDrives()
        else:
            print("Unsupported system " + platform.system() + ", no removable device hotplugging support available.")
            return None
