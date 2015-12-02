# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Resources import Resources

from UM.Math.Matrix import Matrix

from UM.View.RenderPass import RenderPass
from UM.View.GL.OpenGL import OpenGL

class CompositePass(RenderPass):
    def __init__(self, width, height):
        super().__init__("composite", width, height, 999)

        self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "composite.shader"))
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._renderer = Application.getInstance().getRenderer()

        self._layer_bindings = [ "default", "selection" ]

    def setCompositeShader(self, shader):
        self._shader = shader

    def setLayerBindings(self, bindings):
        self._layer_bindings = bindings

    def render(self):
        self._shader.bind()

        step_x = 1 / self._width
        step_y = 1 / self._height
        offset = [
            [-step_x, -step_y], [0.0, -step_y], [step_x, -step_y],
            [-step_x, 0.0],     [0.0, 0.0],     [step_x, 0.0],
            [-step_x, step_y],  [0.0, step_y],  [step_x, step_y]
        ]
        self._shader.setUniformValue("u_offset", offset)

        texture_unit = 0
        for binding in self._layer_bindings:
            render_pass = self._renderer.getRenderPass(binding)
            if not render_pass:
                continue

            self._gl.glActiveTexture(getattr(self._gl, "GL_TEXTURE{0}".format(texture_unit)))
            self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, render_pass.getTextureId())
            texture_unit += 1

        self._renderer.renderFullScreenQuad(self._shader)

        for i in range(texture_unit):
            self._gl.glActiveTexture(getattr(self._gl, "GL_TEXTURE{0}".format(i)))
            self._gl.glBindTexture(self._gl.GL_TEXTURE_2D, 0)

        self._shader.release()

        self._gl.glActiveTexture(self._gl.GL_TEXTURE0)
