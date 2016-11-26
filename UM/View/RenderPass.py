# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger

from UM.View.GL.OpenGL import OpenGL


##  Base class for a rendering pass.
#
#   The RenderPass class encapsulates a render pass, that is a single
#   step in the rendering process.
#
#   \note While the render pass could technically support render to
#   texture without using Framebuffer Objects, the PyQt bindings object
#   lacks support for any function like glReadPixels. Therefore, the
#   Qt OpenGL initialization code checks for FBO support and aborts the
#   program if no support is found.
class RenderPass:
    ##  The maximum priority of a render pass. Priority should always be
    #   less than this.
    MaximumPriority = 999

    def __init__(self, name, width, height, priority = 0):
        self._name = name
        self._width = width
        self._height = height
        self._priority = priority

        self._gl = OpenGL.getInstance().getBindingsObject()

        self._fbo = None

        self._updateRenderStorage()

    ##  Get the name of this RenderPass.
    #
    #   \return \type{string} The name of the render pass.
    def getName(self):
        return self._name

    ##  Get the priority of this RenderPass.
    #
    #   The priority is used for ordering the render passes. Lower priority render passes
    #   are rendered earlier and are available for later render passes to use as texture
    #   sources.
    #
    #   \return \type{int} The priority of this render pass.
    def getPriority(self):
        return self._priority

    ##  Set the size of this render pass.
    #
    #   \param width \type{int} The new width of the render pass.
    #   \param height \type{int} The new height of the render pass.
    #
    #   \note This will recreate the storage object used by the render
    #   pass. Due to that, the contents will be invalid after resizing
    #   until the render pass is rendered again.
    def setSize(self, width, height):
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self._updateRenderStorage()

    ##  Bind the render pass so it can be rendered to.
    #
    #   This will make sure everything is set up so the contents of
    #   this render pass will be updated correctly. It should be called
    #   as part of your render() implementation.
    #
    #   \note It is very important to call release() after a call to
    #   bind(), once done with rendering.
    def bind(self):
        if self._fbo:
            self._fbo.bind()

            # Ensure we can actually write to the relevant FBO components.
            self._gl.glColorMask(self._gl.GL_TRUE, self._gl.GL_TRUE,self._gl.GL_TRUE, self._gl.GL_TRUE)
            self._gl.glDepthMask(self._gl.GL_TRUE)

            self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    ##  Release the render pass.
    #
    #   This makes sure the contents of this render pass are properly
    #   updated at the end of rendering.
    def release(self):
        self._fbo.release()

        # Workaround for a driver bug with recent Intel chips on OSX.
        # Releasing the current FBO does not properly clear the depth buffer, so we have to do that manually.
        #if Platform.isOSX() and OpenGL.getInstance().getGPUVendor() == OpenGL.Vendor.Intel:
            #self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    ##  Render the contents of this render pass.
    #
    #   This method should be reimplemented by subclasses to perform the
    #   actual rendering of the render pass.
    def render(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Get the texture ID of this render pass so it can be reused by other passes.
    #
    #   \return \type{int} The OpenGL texture ID used by this pass.
    def getTextureId(self):
        return self._fbo.getTextureId()

    ##  Get the pixel data produced by this render pass.
    #
    #   This returns an object that contains the pixel data for this render pass.
    #
    #   \note The current object type returned is currently dependant on the specific
    #   implementation of the UM.View.GL.FrameBufferObject class.
    def getOutput(self):
        return self._fbo.getContents()

    ## private:

    def _updateRenderStorage(self):
        if self._width <= 0 or self._height <= 0:
            Logger.log("w", "Tried to create render pass with size <= 0")
            return

        self._fbo = OpenGL.getInstance().createFrameBufferObject(self._width, self._height)
