from UM.View.View import View
from UM.View.Renderer import Renderer
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

class WireframeView(View):
    def __init__(self):
        super().__init__()

    def render(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render(renderer):
                if node.getMeshData():
                    renderer.renderMesh(node.getGlobalTransformation(), node.getMeshData(), Renderer.RenderWireframe)

