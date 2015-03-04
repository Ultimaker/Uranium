from UM.StorageDevice import StorageDevice
from UM.Signal import Signal, SignalEmitter

import platform
import os

class LocalFileStorageDevice(StorageDevice, SignalEmitter):
    def __init__(self):
        super().__init__()
        self._drives = []
        self._removableDrives = self._createRemovableDrives()
        self._removableDrives.drivesChanged.connect(self._onDrivesChanged)
        self._drives = {}

    def openFile(self, file_name, mode):
        return open(file_name, mode)

    def closeFile(self, file):
        file.close()

    def ejectRemovableDrive(self, name):
        if self._removableDrives:
            self._removableDrives.ejectDrive(name)

    def getRemovableDrives(self):
        return self._drives

    removableDrivesChanged = Signal()

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

    def _onDrivesChanged(self, newDrives):
        if len(newDrives) == len(self._drives):
            for key, value in newDrives.items():
                if key not in self._drives:
                    break
                if self._drives[key] != value:
                    break
            else:
                return #No changes in the list of drives, so do nothing.

        self._drives = newDrives
        self.removableDrivesChanged.emit()
