# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot, pyqtSignal, pyqtProperty
from UM.Scene.Selection import Selection

class SceneProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._scene = QCoreApplication.instance().getController().getScene()
        Selection.selectionChanged.connect(self._onSelectionChanged)
    
    selectionChanged = pyqtSignal()
    
    def _onSelectionChanged(self):
        self.selectionChanged.emit()
        
    @pyqtProperty(int, notify = selectionChanged)    
    def numObjectsSelected(self):
        return Selection.getCount()
    
    @pyqtProperty(bool, notify = selectionChanged) 
    def isGroupSelected(self):
        for node in Selection.getAllSelectedObjects():
            if node.callDecoration("isGroup"):
                return True
        return False

    @pyqtSlot(str)
    def setActiveCamera(self, camera):
        self._scene.setActiveCamera(camera)
        
        
    