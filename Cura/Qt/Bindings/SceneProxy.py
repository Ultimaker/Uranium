from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot

class SceneProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._scene = QCoreApplication.instance().getController().getScene()

    @pyqtSlot(str)
    def setActiveCamera(self, camera):
        self._scene.setActiveCamera(camera)
