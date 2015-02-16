from . import SceneNode

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Resources import Resources

class Platform(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

        self._settings = None
        Application.getInstance().activeMachineChanged.connect(self._onActiveMachineChanged)
        self._onActiveMachineChanged()

    def render(self, renderer):
        if self.getMeshData():
            renderer.queueMesh(self.getMeshData(), self.getGlobalTransformation())
            return True

    def _onActiveMachineChanged(self):
        if self._settings:
            self.setMeshData(None)

        app = Application.getInstance()
        self._settings = app.getActiveMachine()
        if self._settings:
            mesh = self._settings.getPlatformMesh()
            self.setMeshData(app.getMeshFileHandler().read(Resources.getPath(Resources.MeshesLocation, mesh), app.getStorageDevice("local")))
