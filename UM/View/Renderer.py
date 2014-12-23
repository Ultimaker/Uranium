##  Abstract base class for different rendering implementations.
#   The renderer can be used to perform rendering of objects. It abstracts away any
#   details about the underlying graphics API that is used to render.
#
#   TODO: Remove get/setController and associate the renderer with a view.
class Renderer():
    RenderTriangles = 1
    RenderLines = 2
    RenderPoints = 3
    RenderWireframe = 4

    def __init__(self, application):
        super().__init__()
        self._application = application

    def getApplication(self):
        return self._application

    ##  Setup the rendering state so we can do correct rendering.
    def preRender(self):
        raise NotImplementedError()

    def renderLines(self, transform, mesh):
        raise NotImplementedError("renderLines should be reimplemented by subclasses")

    ##  Render a mesh using a certain transformation matrix.
    #   \param transform The transformation matrix to use to render the mesh.
    #   \param mesh The MeshData object to render.
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - material: The material to use to render. By default this is a standard grey lighted material.
    #                 - mode: The mode to render in. By default this is Renderer.RenderTriangles.
    def renderMesh(self, transform, mesh, **kwargs):
        raise NotImplementedError("renderMesh should be reimplemented by subclasses")

    ##  Create an instance of a renderer-specific subclass of Material
    def createMaterial(self):
        raise NotImplementedError()
