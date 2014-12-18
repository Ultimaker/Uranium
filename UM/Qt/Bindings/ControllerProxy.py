from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot, QUrl

from UM.Application import Application
from UM.Scene.SceneNode import SceneNode
from UM.Scene.BoxRenderer import BoxRenderer

from UM.Operations.AddMeshOperation import AddMeshOperation

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

        app = Application.getInstance()

        op = AddMeshOperation(app.getMeshFileHandler().read(file_name.toLocalFile(), app.getStorageDevice('local')), self._controller.getScene().getRoot())
        app.getOperationStack().push(op)
