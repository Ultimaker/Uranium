# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Application import Application
from UM.Resources import Resources
from UM.Math.Color import Color

from UM.View.RenderPass import RenderPass
from UM.View.GL.OpenGL import OpenGL

from typing import List

MYPY = False
if MYPY:
    from UM.View.GL.ShaderProgram import ShaderProgram


class CompositePass(RenderPass):
    """A RenderPass subclass providing the final composition render.

    This render pass uses the other render passes to render a final composited image.
    By default, this consists of the output of the default pass, with an outline
    rendered on top of it using a convolution filter.

    You can use setCompositeShader() to override the shader used for the composition.
    Additionally, setLayerBindings() can be used to set layer bindings, that is set,
    which layer is bound to which texture unit.

    :note The CompositePass should always be last in the Renderer's rendering order.
    Therefore, when subclassing RenderPass make sure to use a priority lower than
    RenderPass.MaximumPriority.
    """
    def __init__(self, width, height):
        super().__init__("composite", width, height, RenderPass.MaximumPriority)

        self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "composite.shader"))
        theme = Application.getInstance().getTheme()
        self._shader.setUniformValue("u_background_color", Color(*theme.getColor("viewport_background").getRgb()))
        self._shader.setUniformValue("u_outline_color", Color(*theme.getColor("model_selection_outline").getRgb()))

        self._gl = OpenGL.getInstance().getBindingsObject()
        self._renderer = Application.getInstance().getRenderer()

        self._layer_bindings = ["default", "selection"]

    def getCompositeShader(self) -> "ShaderProgram":
        """Get the shader currently used for compositing."""
        return self._shader

    def setCompositeShader(self, shader: "ShaderProgram") -> None:
        """Set the shader to use for compositing."""
        self._shader = shader

    def getLayerBindings(self) -> List[str]:
        """Get the current layer bindings."""
        return self._layer_bindings

    def setLayerBindings(self, bindings: List[str]) -> None:
        """Set the layer bindings to use.

        This should be a list of RenderPass names. The passes will be bound
        to different texture units in the order specified. By default, the output
        of the "default" RenderPass is bound to texture unit 0 and the output of
        the "selection" RenderPass is bound to texture unit 1.

        :param bindings: The list of layer bindings to use.
        """
        self._layer_bindings = bindings

    def render(self) -> None:
        """Perform the actual rendering of the render pass."""
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
