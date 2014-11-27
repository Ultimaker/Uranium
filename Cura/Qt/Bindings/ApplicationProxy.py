from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot

class ApplicationProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._application = QCoreApplication.instance()

    @pyqtSlot(str, str)
    def log(self, type, message):
        self._application.log(type, message)
