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
    RenderLineLoop = 5

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

    ##  Queue a node to be rendered.
    #
    #   \param node The node to queue for rendering.
    #   \param kwargs Keyword arguments.
    #                 Possible keywords:
    #                 - mesh: A different mesh from the node's MeshData to use for rendering.
    #                 - material: The material to use to render. By default this is a standard grey lighted material.
    #                 - mode: The mode to render in. By default this is Renderer.RenderTriangles.
    #                 - transparent: Should this mesh be rendered with transparency. Boolean value, default False.
    #                 - overlay: Should this mesh be rendered on top of everything else. Boolean value, default False.
    def queueNode(self, node, **kwargs):
        raise NotImplementedError()

    ##  Render all queued meshes, in an order specified by the renderer.
    def renderQueuedNodes(self):
        raise NotImplementedError()

    ##  Finish rendering, finalize and clear state.
    def endRendering(self):
        raise NotImplementedError()
