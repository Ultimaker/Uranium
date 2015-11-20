# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import sys
import ctypes

from UM.View.OpenGL import OpenGL

class RenderPass:
    def __init__(self):
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._fbo = OpenGL.getInstance().createFrameBufferObject()

        self._texture = None
        if not self._fbo:
            self._texture = OpenGL.getInstance().createTexture()
        else:
            self._texture = self._fbo.getTexture()

    def bind(self):
        if self._fbo:
            self._fbo.bind()

    def release(self):
        if self._fbo:
            self._fbo.release()

            # Workaround for a driver bug with recent Intel chips on OSX.
            # Releasing the current FBO does not properly clear the depth buffer, so we have to do that manually.
            if sys.platform == "darwin" and OpenGL.getInstance().getGPUVendor() == OpenGL.Vendor.Intel:
                self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
        else:
            self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, self._texture)
            self._gl.glCopyTexImage2D(self._gl.GL_TEXTURE_2D, 0, self._gl.GL_RGBA, 0, 0, self._width, self._height, 0)
            self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, 0)
            self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    def render(self):
        raise NotImplementedError("Should be implemented by subclasses")

    def getOutput(self):
        data = ctypes.

        self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, self._texture)
        self._gl.glGetTexImage(self._gl.GL_TEXTURE_2D, 0, self._gl.GL_RGBA, self._gl.GL_UNSIGNED_INT, data)
        self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, 0)
        return data
