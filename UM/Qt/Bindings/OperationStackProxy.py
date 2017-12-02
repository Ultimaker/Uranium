# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Application import Application

class OperationStackProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._operation_stack = Application.getInstance().getOperationStack()
        self._operation_stack.changed.connect(self._onUndoStackChanged)

    undoStackChanged = pyqtSignal()

    @pyqtProperty(bool, notify=undoStackChanged)
    def canUndo(self):
        return self._operation_stack.canUndo()

    @pyqtProperty(bool, notify=undoStackChanged)
    def canRedo(self):
        return self._operation_stack.canRedo()

    @pyqtSlot()
    def undo(self):
        self._operation_stack.undo()

    @pyqtSlot()
    def redo(self):
        self._operation_stack.redo()

    def _onUndoStackChanged(self):
        self.undoStackChanged.emit()
