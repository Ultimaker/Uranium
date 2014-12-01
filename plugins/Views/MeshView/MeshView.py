from Cura.View.View import View
from Cura.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

class MeshView(View):
    def __init__(self):
        super().__init__()

    def render(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render():
                if node.getMeshData():
                    renderer.renderMesh(node.getGlobalTransformation(), node.getMeshData())
