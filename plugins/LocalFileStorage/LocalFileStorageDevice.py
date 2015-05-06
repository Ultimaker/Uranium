# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.StorageDevice import StorageDevice
from UM.Signal import Signal, SignalEmitter
from UM.Logger import Logger

import platform
import os
import copy

class LocalFileStorageDevice(StorageDevice, SignalEmitter):
    def __init__(self):
        super().__init__()
        self._drives = []
        self._removable_drives = self._createRemovableDrives()
        self._removable_drives.drivesChanged.connect(self._onDrivesChanged)
        self._drives = {}

    def openFile(self, file_name, mode):
        return open(file_name, mode)

    def closeFile(self, file):
        file.close()

    def ejectRemovableDrive(self, name):
        if self._removable_drives and name in self._drives:
            self._removable_drives.ejectDrive(name, self._drives[name])

    def getRemovableDrives(self):
        return copy.deepcopy(self._drives)

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
            Logger.log("e", "Unsupported system %s, no removable device hotplugging support available.", platform.system())
            return None

    def _onDrivesChanged(self, new_drives):
        if len(new_drives) == len(self._drives):
            for key, value in new_drives.items():
                if key not in self._drives:
                    break
                if self._drives[key] != value:
                    break
            else:
                return #No changes in the list of drives, so do nothing.

        self._drives = new_drives
        self.removableDrivesChanged.emit()
