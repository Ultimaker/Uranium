from Cura.View.View import View
from Cura.View.Renderer import Renderer

class WireframeView(View):
    def __init__(self):
        super().__init__()

    def render(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        self._renderObject(scene.getRoot(), renderer)

    def _renderObject(self, object, renderer):
        if not object.render():
            if object.getMeshData():
                renderer.renderMesh(object.getGlobalTransformation(), object.getMeshData(), Renderer.RenderLines)

        for child in object.getChildren():
            self._renderObject(child, renderer)
