from PyQt5.QtCore import QObject, QCoreApplication, pyqtSlot, QUrl

from UM.Application import Application
from UM.Scene.SceneNode import SceneNode
from UM.Scene.BoxRenderer import BoxRenderer
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Mesh.LoadMeshJob import LoadMeshJob

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

        node = SceneNode()
        node.setSelectionMask(1)

        op = AddSceneNodeOperation(node, self._controller.getScene().getRoot())
        app.getOperationStack().push(op)

        job = LoadMeshJob(node, file_name.toLocalFile())
        job.finished.connect(self._loadMeshFinished)
        job.start()

    def _loadMeshFinished(self, job):
        job.getNode().setMeshData(job.getResult())
        self._controller.getScene().sceneChanged.emit(job.getNode())
