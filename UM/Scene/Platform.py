from . import SceneNode

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Resources import Resources

class Platform(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

        app = Application.getInstance()
        mesh = app.getInstance().getMachineSettings().getPlatformMesh()
        if mesh is not None:
            self.setMeshData(app.getMeshFileHandler().read(Resources.getPath(Resources.MeshesLocation, mesh), app.getStorageDevice("local")))

    def render(self, renderer):
        if self.getMeshData():
            renderer.queueMesh(self.getMeshData(), self.getGlobalTransformation())
            return True
