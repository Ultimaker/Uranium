from . import SceneNode

from UM.View.Renderer import Renderer

class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = "Pointcloud"

    def render(self, renderer):
        if self.getMeshData() and self.isVisible():
            renderer.queueMesh(self.getMeshData(), self.getGlobalTransformation(), mode = Renderer.RenderPoints)
            return True
