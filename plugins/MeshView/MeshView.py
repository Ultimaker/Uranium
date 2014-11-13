from Cura.View.View import View

class MeshView(View):
    def __init__(self):
        super(MeshView, self).__init__()

    def render(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        self._renderObject(scene.getRoot(), renderer)

    def _renderObject(self, object, renderer):
        if object.getMeshData():
            renderer.renderMesh(object.getGlobalTransformation(), object.getMeshData())

        for child in object.getChildren():
            self._renderObject(child, renderer)
