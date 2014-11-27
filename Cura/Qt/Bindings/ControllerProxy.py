from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot

class ControllerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = QCoreApplication.instance().getController()

    @pyqtSlot(str)
    def setActiveView(self, view):
        self._controller.setActiveView(view)

    @pyqtSlot(str)
    def setActiveTool(self, tool):
        self._controller.setActiveTool(tool)
