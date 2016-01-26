from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ContainerProxy(QObject):
    def __init__(self, container, parent = None):
        super().__init__(parent)

        self._container = container

    @pyqtSlot(str, result = "QVariant")
    def getValue(self, value):
        return self._container.get(value, None)

    @pyqtSlot(str, "QVariant")
    def setValue(self, key, value):
        self._container[key] = value

    @pyqtSlot(result = int)
    def getCount(self):
        return len(self._container)
