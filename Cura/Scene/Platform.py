from . import SceneNode

from Cura.Application import Application
from Cura.View.Renderer import Renderer
from Cura.Resources import Resources

class Platform(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

        app = Application.getInstance()
        mesh = app.getInstance().getMachineSettings().getPlatformMesh()
        if mesh is not None:
            self.setMeshData(app.getMeshFileHandler().read(Resources.locate(Resources.MeshesLocation, mesh), app.getStorageDevice("local")))

    def render(self, renderer):
        if self.getMeshData():
            renderer.renderMesh(self.getGlobalTransformation(), self.getMeshData(), Renderer.RenderTriangles)
            return True
