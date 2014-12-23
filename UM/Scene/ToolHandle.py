from . import SceneNode

from UM.View.Renderer import Renderer
from UM.Mesh.MeshData import MeshData

class ToolHandle(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setMeshData(MeshData())
        self._material = None

    def render(self, renderer):
        renderer.queueMesh(self.getMeshData(), self.getGlobalTransformation(), mode = Renderer.RenderLines, overlay = True)
        return True
