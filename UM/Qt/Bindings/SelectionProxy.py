# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from UM.Application import Application
from UM.Scene.Selection import Selection

class SelectionProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        Selection.selectionChanged.connect(self._onSelectionChanged)
        Selection.selectedFaceChanged.connect(self._onSelectedFaceChanged)

    selectionChanged = pyqtSignal()
    selectedFaceChanged = pyqtSignal()

    @pyqtProperty(bool, notify = selectionChanged)
    def hasSelection(self):
        return Selection.hasSelection()

    @pyqtProperty(bool, notify = selectedFaceChanged)
    def faceSelectMode(self):
        return Selection.getFaceSelectMode()

    @pyqtSlot(bool)
    def setFaceSelectMode(self, select: bool) -> None:
        Selection.setFaceSelectMode(select)
        if not select:
            Selection.clearFace()

    @pyqtProperty(bool, notify = selectedFaceChanged)
    def hasFaceSelected(self):
        return Selection.getSelectedFace() is not None

    @pyqtProperty(int, notify = selectionChanged)
    def selectionCount(self):
        return Selection.getCount()

    @pyqtProperty("QVariantList", notify = selectionChanged)
    def selectionNames(self):
        return [node.getName() for node in Selection.getAllSelectedObjects()]

    def _onSelectionChanged(self):
        self.selectionChanged.emit()

    def _onSelectedFaceChanged(self):
        self.selectedFaceChanged.emit()

    @pyqtProperty(bool, notify=selectionChanged)
    def isGroupSelected(self):
        for node in Selection.getAllSelectedObjects():
            if node.callDecoration("isGroup"):
                return True
        return False

def createSelectionProxy(engine, script_engine):
    return SelectionProxy()
