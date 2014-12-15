from . import SceneNode

from UM.View.Renderer import Renderer
from UM.MeshHandling.MeshData import MeshData

class ToolHandle(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setMeshData(MeshData())

    def render(self, renderer):
        renderer.setDepthTesting(False)
        renderer.renderLines(self.getGlobalTransformation(), self.getMeshData())
        renderer.setDepthTesting(True)
        return True
