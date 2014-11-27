from PyQt5.QtCore import QObject, QCoreApplication

class BackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = QCoreApplication.instance().getBackend()
