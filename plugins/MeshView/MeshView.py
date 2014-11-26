from Cura.View.View import View
from Cura.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

class MeshView(View):
    def __init__(self):
        super(MeshView, self).__init__()

    def render(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()
        print("Herpaderp")
        self._renderObject(scene.getRoot(), renderer)

    def _renderObject(self, object, renderer):
        for node in DepthFirstIterator(object):
            if not node.render():
                if node.getMeshData():
                    renderer.renderMesh(node.getGlobalTransformation(), node.getMeshData())
