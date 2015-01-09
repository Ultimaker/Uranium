from . import SceneNode

from UM.View.Renderer import Renderer

class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

    def render(self, renderer):
        if self.getMeshData() and self.isVisible():
            renderer.queueMesh(self.getMeshData(), self.getGlobalTransformation(), mode = Renderer.RenderPoints)
            return True
