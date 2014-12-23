##  Abstract base class for different rendering implementations.
#
#   The renderer is used to perform rendering of objects. It abstracts away any
#   details about the underlying graphics API that is used to render. It is designed
#   to perform different stages of rendering, with the application indicating which
#   objects should be rendered but the actual rendering process happening after a
#   sorting step.
class Renderer():
    RenderTriangles = 1
    RenderLines = 2
    RenderPoints = 3
    RenderWireframe = 4

    def __init__(self):
        super().__init__()

    ##  Create an instance of a renderer-specific subclass of Material
    def createMaterial(self):
        raise NotImplementedError()

    ##  Signal the beginning of the rendering process.
    #
    #   This should set up any required state before any actual rendering happens.
    def beginRendering(self):
        raise NotImplementedError()

    ##  Queue a mesh to be rendered.
    #
    #   \param mesh The mesh to queue for rendering.
    #   \param transform The transformation matrix to apply to the mesh.
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - material: The material to use to render. By default this is a standard grey lighted material.
    #                 - mode: The mode to render in. By default this is Renderer.RenderTriangles.
    #                 - transparent: Should this mesh be rendered with transparency. Boolean value, default False.
    #                 - overlay: Should this mesh be rendered on top of everything else. Boolean value, default False.
    def queueMesh(self, transform, mesh, **kwargs):
        raise NotImplementedError()

    ##  Render all queued meshes, in an order specified by the renderer.
    def renderQueuedMeshes(self):
        raise NotImplementedError()

    ##  Finish rendering, finalize and clear state.
    def endRendering(self):
        raise NotImplementedError()
