from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application
from UM.Logger import Logger

class ApplicationProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._application = Application.getInstance()
        self._application.activeMachineChanged.connect(self._onActiveMachineChanged)

    @pyqtSlot(str, str)
    def log(self, type, message):
        Logger.log(type, message)

    machineChanged = pyqtSignal()

    @pyqtProperty(str, notify=machineChanged)
    def machineName(self):
        if self._application.getActiveMachine():
            return self._application.getActiveMachine().getName()

    @pyqtProperty(str, notify=machineChanged)
    def machineIcon(self):
        if self._application.getActiveMachine():
            return self._application.getActiveMachine().getIcon()

    def _onActiveMachineChanged(self):
        self.machineChanged.emit()
