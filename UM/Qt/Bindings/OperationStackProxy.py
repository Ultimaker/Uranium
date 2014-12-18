from PyQt5.QtCore import QObject, pyqtSlot

from UM.Application import Application

class OperationStackProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._operation_stack = Application.getInstance().getOperationStack()

    @pyqtSlot()
    def undo(self):
        self._operation_stack.undo()

    @pyqtSlot()
    def redo(self):
        self._operation_stack.redo()
