from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot, QUrl

from Cura.Application import Application
from Cura.Scene.SceneNode import SceneNode

class ControllerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()

    @pyqtSlot(str)
    def setActiveView(self, view):
        self._controller.setActiveView(view)

    @pyqtSlot(str)
    def setActiveTool(self, tool):
        self._controller.setActiveTool(tool)

    @pyqtSlot(QUrl)
    def addMesh(self, file_name):
        if not file_name.isValid():
            return

        mesh = SceneNode(self._controller.getScene().getRoot())
        app = Application.getInstance()
        mesh.setMeshData(app.getMeshFileHandler().read(file_name.toLocalFile(), app.getStorageDevice('local')))
