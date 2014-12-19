from . import SceneNode

from UM.View.Renderer import Renderer

class PointCloudNode(SceneNode.SceneNode):
    def __init__(self, parent):
        super().__init__(parent)

    def render(self, renderer):
        if self.getMeshData():

            renderer.renderMesh(self.getGlobalTransformation(), self.getMeshData(), Renderer.RenderPoints)
            return True
