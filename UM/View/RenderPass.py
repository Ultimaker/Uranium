# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import sys
import ctypes

from UM.Application import Application
from UM.Logger import Logger
from UM.Platform import Platform

from UM.View.GL.OpenGL import OpenGL

class RenderPass:
    def __init__(self, name, width, height, priority = 0):
        self._name = name
        self._width = width
        self._height = height
        self._priority = priority

        self._gl = OpenGL.getInstance().getBindingsObject()

        self._fbo = None
        self._texture = None

        self._updateRenderStorage()

        if self._fbo:
            self.release = self._releaseFBO
        else:
            self.release = self._releaseTexture

    def getName(self):
        return self._name

    def getPriority(self):
        return self._priority

    ##  Set the size of this render pass.
    def setSize(self, width, height):
        if self._width != width or self._height != height:
            self._width = width
            self._height = height
            self._updateRenderStorage()

    ##  Bind the render pass so it can be rendered to
    def bind(self):
        if self._fbo:
            self._fbo.bind()

    ##  Release the render pass
    def release(self):
        # Note that this is dynamically bound to either _releaseFBO or _releaseTexture based on FBO availability
        pass

    ##  Render the contents of this render pass.
    def renderContents(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Render the output of this render pass.
    def renderOutput(self):
        raise NotImplementedError("Should be implemented by subclasses")

    ##  Get the texture ID of this render pass so it can be reused by other passes.
    def getTextureId(self):
        return self._fbo.getTextureId() if self._fbo else self._texture.getTextureId()

    ##  Get the pixel data produced by this render pass
    def getOutput(self):
        data = ctypes.c_uint32 * self._width * self._height;

        texture = self.getTextureId()

        self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, texture)
        self._gl.glGetTexImage(self._gl.GL_TEXTURE_2D, 0, self._gl.GL_RGBA, self._gl.GL_UNSIGNED_INT, data)
        self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, 0)

        return data

    def renderBatches(self, **kwargs):
        for batch in Application.getInstance().getRenderer().getBatches():
            batch.render()

    ## private:

    def _updateRenderStorage(self):
        if self._width <= 0 or self._height <= 0:
            Logger.log("w", "Tried to create render pass with size <= 0")
            return

        if OpenGL.getInstance().hasFrameBufferObjects():
            self._fbo = OpenGL.getInstance().createFrameBufferObject(self._width, self._height)
        else:
            self._texture = OpenGL.getInstance().createTexture(self._width, self._height)

    def _releaseFBO(self):
        self._fbo.release()

        # Workaround for a driver bug with recent Intel chips on OSX.
        # Releasing the current FBO does not properly clear the depth buffer, so we have to do that manually.
        #if Platform.isOSX() and OpenGL.getInstance().getGPUVendor() == OpenGL.Vendor.Intel:
            #self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    def _releaseTexture(self):
        self._texture.bind()
        self._gl.glCopyTexImage2D(self._gl.GL_TEXTURE_2D, 0, self._gl.GL_RGBA, 0, 0, self._width, self._height, 0)
        self._texture.release()
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
