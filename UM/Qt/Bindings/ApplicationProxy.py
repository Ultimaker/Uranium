# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Logger import Logger


class ApplicationProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._application = Application.getInstance()

    @pyqtProperty(str, constant = True)
    def version(self):
        return self._application.getVersion()

