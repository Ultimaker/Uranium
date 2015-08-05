# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Logger import Logger

import platform

class ApplicationProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._application = Application.getInstance()

    @pyqtSlot(str, str)
    def log(self, type, message):
        Logger.log(type, message)

    @pyqtProperty(str, constant = True)
    def version(self):
        return self._application.getVersion()

    machineChanged = pyqtSignal()

    @pyqtProperty(str, notify=machineChanged)
    def machineName(self):
        return ""
