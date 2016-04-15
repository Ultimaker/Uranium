# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Resources import Resources

from UM.View.RenderPass import RenderPass
from UM.View.GL.OpenGL import OpenGL


##  A RenderPass subclass providing the final composition render.
#
#   This render pass uses the other render passes to render a final composited image.
#   By default, this consists of the output of the default pass, with an outline
#   rendered on top of it using a convolution filter.
#
#   You can use setCompositeShader() to override the shader used for the composition.
#   Additionally, setLayerBindings() can be used to set layer bindings, that is set,
#   which layer is bound to which texture unit.
#
#   \note The CompositePass should always be last in the Renderer's rendering order.
#   Therefore, when subclassing RenderPass make sure to use a priority lower than
#   RenderPass.MaximumPriority.
class CompositePass(RenderPass):
    def __init__(self, width, height):
        super().__init__("composite", width, height, RenderPass.MaximumPriority)

        self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "composite.shader"))
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._renderer = Application.getInstance().getRenderer()

        self._layer_bindings = [ "default", "selection" ]

    ##  Get the shader currently used for compositing.
    def getCompositeShader(self):
        return self._shader

    ##  Set the shader to use for compositing.
    def setCompositeShader(self, shader):
        self._shader = shader

    ##  Get the current layer bindings.
    def getLayerBindings(self):
        return self._layer_bindings

    ##  Set the layer bindings to use.
    #
    #   This should be a list of RenderPass names. The passes will be bound
    #   to different texture units in the order specified. By default, the output
    #   of the "default" RenderPass is bound to texture unit 0 and the output of
    #   the "selection" RenderPass is bound to texture unit 1.
    #
    #   \param bindings The list of layer bindings to use.
    def setLayerBindings(self, bindings):
        self._layer_bindings = bindings

    ##  Perform the actual rendering of the render pass.
    def render(self):
        self._shader.bind()

        outline_size = 2.0

        step_x = outline_size / self._width
        step_y = outline_size / self._height
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
