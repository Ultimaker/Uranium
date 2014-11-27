##  Abstract base class for different rendering implementations.
#   The renderer can be used to perform rendering of objects. It abstracts away any
#   details about the underlying graphics API that is used to render.
#
#   TODO: Remove get/setController and associate the renderer with a view.
class Renderer(object):
    RenderTriangles = 1
    RenderLines = 2
    RenderPoints = 3

    def __init__(self):
        super(Renderer, self).__init__()
        self._controller = None

    ##  Initialize the renderer.
    #   This can be reimplemented to allow the renderer to setup any needed resources.
    def initialize(self):
        pass

    ##  Render a mesh using a certain transformation matrix.
    #   \param transform The transformation matrix to use to render the mesh.
    #   \param mesh The MeshData object to render.
    def renderMesh(self, transform, mesh, mode = RenderTriangles):
        raise NotImplementedError("renderMesh should be reimplemented by subclasses")

    ##  Get the controller associated with this renderer.
    def getController(self):
        return self._controller

    ##  Set the controller to use with this renderer.
    def setController(self, controller):
        self._controller = controller
