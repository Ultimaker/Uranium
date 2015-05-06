# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot

class SceneProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._scene = QCoreApplication.instance().getController().getScene()

    @pyqtSlot(str)
    def setActiveCamera(self, camera):
        self._scene.setActiveCamera(camera)
