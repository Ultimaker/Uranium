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

    ##  Initialize the renderer.
    #   This can be reimplemented to allow the renderer to setup any needed resources.
    def initialize(self):
        pass

    def renderLines(self, transform, mesh):
        raise NotImplementedError("renderLines should be reimplemented by subclasses")

    ##  Render a mesh using a certain transformation matrix.
    #   \param transform The transformation matrix to use to render the mesh.
    #   \param mesh The MeshData object to render.
    def renderMesh(self, transform, mesh, mode = RenderTriangles):
        raise NotImplementedError("renderMesh should be reimplemented by subclasses")

    def setDepthTesting(self, depthTesting):
        raise NotImplementedError("setDepthTesting should be reimplemented by subclasses")
