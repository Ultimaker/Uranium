from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Logger import Logger

class ApplicationProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._application = Application.getInstance()

    @pyqtSlot(str, str)
    def log(self, type, message):
        Logger.log(type, message)

    machineChanged = pyqtSignal()

    @pyqtProperty(str, notify=machineChanged)
    def machineName(self):
        return self._application.getMachineSettings().getName()

    @pyqtProperty(str)
    def machineIcon(self, notify=machineChanged):
        return self._application.getMachineSettings().getIcon()
