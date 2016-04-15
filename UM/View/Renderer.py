# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.SortedList import SortedListWithKey


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

        self._render_passes = SortedListWithKey(key = lambda k: k.getPriority())

    ##  Signal the beginning of the rendering process.
    #
    #   This should set up any required state before any actual rendering happens.
    def beginRendering(self):
        raise NotImplementedError()

    ##  Queue a node to be rendered.
    #
    #   \param node The node to queue for rendering.
    #   \param kwargs Keyword arguments.
    #                 Most of these are passed to the RenderBatch constructor directly. See RenderBatch for all available options.
    #                 In addition, the parameter "shader" is available, which determines the shader to render with. When not specified,
    #                 it defaults to a simple vertex color shader.
    def queueNode(self, node, **kwargs):
        raise NotImplementedError()

    ##  Render everything that was set up to be rendered.
    def render(self):
        raise NotImplementedError()

    ##  Finish rendering, finalize and clear state.
    def endRendering(self):
        raise NotImplementedError()

    ##  Add a render pass that should be rendered.
    #
    #   \param render_pass The render pass to add.
    def addRenderPass(self, render_pass):
        self._render_passes.add(render_pass)

    ##  Remove a render pass from the list of render passes to render.
    #
    #   \param render_pass The render pass to remove.
    def removeRenderPass(self, render_pass):
        if render_pass in self._render_passes:
            self._render_passes.remove(render_pass)

    ##  Get a render pass by name.
    #
    #   \param name The name of the render pass to get.
    #
    #   \return The named render pass or None if not found.
    def getRenderPass(self, name):
        for render_pass in self._render_passes:
            if render_pass.getName() == name:
                return render_pass

        return None

    ##  Get the list of all render passes that should be rendered.
    def getRenderPasses(self):
        return self._render_passes
