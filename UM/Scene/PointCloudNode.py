from . import SceneNode

from UM.View.Renderer import Renderer

class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = "Pointcloud"
        self._selectable = False

    def render(self, renderer):
        if self.getMeshData() and self.isVisible():
            renderer.queueNode(self, mode = Renderer.RenderPoints)
            return True
