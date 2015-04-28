from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty

from UM.Application import Application

class BackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = Application.getInstance().getBackend()
        self._progress = -1;
        if self._backend:
            self._backend.processingProgress.connect(self._onProcessingProgress)

    processingProgress = pyqtSignal(float, arguments = ['amount'])
    
    @pyqtProperty(float, notify = processingProgress)
    def progress(self):
        return self._progress

    def _onProcessingProgress(self, amount):
        self._progress = amount
        self.processingProgress.emit(amount)
