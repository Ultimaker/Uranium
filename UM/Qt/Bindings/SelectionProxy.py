# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from UM.Application import Application
from UM.Scene.Selection import Selection

class SelectionProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        Selection.selectionChanged.connect(self._onSelectionChanged)

    selectionChanged = pyqtSignal()

    @pyqtProperty(bool, notify = selectionChanged)
    def hasSelection(self):
        return Selection.hasSelection()

    @pyqtProperty(int, notify = selectionChanged)
    def selectionCount(self):
        return Selection.getCount()

    @pyqtProperty("QVariantList", notify = selectionChanged)
    def selectionNames(self):
        return [node.getName() for node in Selection.getAllSelectedObjects()]

    def _onSelectionChanged(self):
        self.selectionChanged.emit()

def createSelectionProxy(engine, script_engine):
    return SelectionProxy()
