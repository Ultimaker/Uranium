# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Resources import Resources

from UM.Math.Matrix import Matrix

from UM.View.RenderPass import RenderPass
from UM.View.GL.OpenGL import OpenGL

class CompositePass(RenderPass):
    def __init__(self, width, height):
        super().__init__("composite", width, height)

        self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "composite.shader"))
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._renderer = Application.getInstance().getRenderer()

    def setCompositeShader(self, shader):
        self._shader = shader

    def renderContents(self):
        pass

    def renderOutput(self):
        self._shader.bind()

        texture_unit = 0
        for render_pass in self._renderer.getRenderPasses():
            self._gl.glActiveTexture(texture_unit)
            self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, render_pass.getTextureId())
            texture_unit += 1

        self._renderer.renderQuad(self._shader)

        for i in range(texture_unit):
            self._gl.glActiveTexture(texture_unit)
            self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, 0)

        self._shader.release()
