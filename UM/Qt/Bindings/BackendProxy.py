from PyQt5.QtCore import QObject, pyqtSignal

from UM.Application import Application

class BackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = Application.getInstance().getBackend()
        if self._backend:
            self._backend.processingProgress.connect(self._onProcessingProgress)

    processingProgress = pyqtSignal(float, arguments = ['amount'])

    def _onProcessingProgress(self, amount):
        self.processingProgress.emit(amount)
