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

        job = LoadMeshJob(file_name.toLocalFile())
        job.finished.connect(self._loadMeshFinished)
        job.start()

    def _loadMeshFinished(self, job):
        node = SceneNode(self._controller.getScene().getRoot())
        node.setSelectionMask(1)
        node.setMeshData(job.getResult())

        op = AddSceneNodeOperation(node, self._controller.getScene().getRoot())
        Application.getInstance().getOperationStack().push(op)
