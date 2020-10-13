# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import numpy
from PyQt5.QtGui import QColor, QOpenGLBuffer, QOpenGLVertexArrayObject
from typing import List, Tuple, Dict

import UM.Qt.QtApplication
from UM.View.Renderer import Renderer
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Resources import Resources

from UM.View.CompositePass import CompositePass
from UM.View.DefaultPass import DefaultPass
from UM.View.SelectionPass import SelectionPass
from UM.View.GL.OpenGL import OpenGL
from UM.View.GL.OpenGLContext import OpenGLContext
from UM.View.RenderBatch import RenderBatch

from UM.Signal import Signal, signalemitter

from UM.Logger import Logger

MYPY = False
if MYPY:
    from UM.Scene.SceneNode import SceneNode
    from UM.View.RenderPass import RenderPass
    from UM.View.GL.ShaderProgram import ShaderProgram


vertexBufferProperty = "__qtgl2_vertex_buffer"
indexBufferProperty = "__qtgl2_index_buffer"


@signalemitter
class QtRenderer(Renderer):
    """A Renderer implementation using PyQt's OpenGL implementation to render."""

    def __init__(self) -> None:
        super().__init__()

        self._initialized = False  # type: bool

        self._light_position = Vector(0, 0, 0)  # type: Vector
        self._background_color = QColor(128, 128, 128)  # type: QColor
        self._viewport_width = 0  # type: int
        self._viewport_height = 0  # type: int
        self._window_width = 0  # type: int
        self._window_height = 0  # type: int

        self._batches = []  # type: List[RenderBatch]
        self._named_batches = {}  # type: Dict[str, RenderBatch]
        self._quad_buffer = None  # type: QOpenGLBuffer

    initialized = Signal()

    @staticmethod
    def getPixelMultiplier() -> int:
        """Get an integer multiplier that can be used to correct for screen DPI."""

        # Standard assumption for screen pixel density is 96 DPI. We use that as baseline to get
        # a multiplication factor we can use for screens > 96 DPI.
        return round(UM.Qt.QtApplication.QtApplication.getInstance().primaryScreen().physicalDotsPerInch() / 96.0)

    def getBatches(self) -> List[RenderBatch]:
        """Get the list of render batches."""

        return self._batches

    def addRenderBatch(self, render_batch, name = ""):
        self._batches.append(render_batch)
        if name:
            self._named_batches[name] = render_batch

    def getNamedBatch(self, name):
        return self._named_batches.get(name)

    def addRenderPass(self, render_pass: "RenderPass") -> None:
        """Overridden from Renderer.

        This makes sure the added render pass has the right size.
        """

        super().addRenderPass(render_pass)
        render_pass.setSize(self._viewport_width, self._viewport_height)

    def setBackgroundColor(self, color: QColor) -> None:
        """Set background color used when rendering."""

        self._background_color = color

    def getViewportWidth(self) -> int:
        return self._viewport_width

    def getViewportHeight(self) -> int:
        return self._viewport_height

    def setViewportSize(self, width: int, height: int) -> None:
        """Set the viewport size.

        :param width: The new width of the viewport.
        :param height: The new height of the viewport.
        """

        self._viewport_width = width
        self._viewport_height = height

        for render_pass in self._render_passes:
            render_pass.setSize(width, height)

    def setWindowSize(self, width: int, height: int) -> None:
        """Set the window size."""

        self._window_width = width
        self._window_height = height

    def getWindowSize(self) -> Tuple[int, int]:
        """Get the window size.

        :return: A tuple of (window_width, window_height)
        """

        return self._window_width, self._window_height

    def beginRendering(self) -> None:
        """Overrides Renderer::beginRendering()"""

        if not self._initialized:
            self._initialize()

        self._gl.glViewport(0, 0, self._viewport_width, self._viewport_height)
        self._gl.glClearColor(self._background_color.redF(), self._background_color.greenF(), self._background_color.blueF(), self._background_color.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
        self._gl.glClearColor(0.0, 0.0, 0.0, 0.0)

    def queueNode(self, node: "SceneNode", **kwargs) -> None:
        """Overrides Renderer::queueNode()"""
        batch = self.createRenderBatch(**kwargs)

        batch.addItem(node.getWorldTransformation(copy = False), kwargs.get("mesh", node.getMeshData()), kwargs.pop("uniforms", None), normal_transformation=node.getCachedNormalMatrix())

        self._batches.append(batch)

    def createRenderBatch(self, **kwargs):
        type = kwargs.pop("type", RenderBatch.RenderType.Solid)
        if kwargs.pop("transparent", False):
            type = RenderBatch.RenderType.Transparent
        elif kwargs.pop("overlay", False):
            type = RenderBatch.RenderType.Overlay

        shader = kwargs.pop("shader", self._default_material)
        return RenderBatch(shader, type=type, **kwargs)

    def render(self) -> None:
        """Overrides Renderer::render()"""

        self._batches.sort()

        for render_pass in self.getRenderPasses():
            width, height = render_pass.getSize()
            self._gl.glViewport(0, 0, width, height)
            render_pass.render()

    def reRenderLast(self):
        """Sometimes not an *entire* new render is required (QML is updated, but the scene did not).
        In that case we ask the composite pass (which must be the last render pass) to render (instead of re-rendering
        all the passes & the views.
        """

        self.beginRendering() # First ensure that the viewport is set correctly.
        self.getRenderPasses()[-1].render()

    def endRendering(self) -> None:
        """Overrides Renderer::endRendering()"""

        self._batches.clear()
        self._named_batches.clear()

    def renderFullScreenQuad(self, shader: "ShaderProgram") -> None:
        """Render a full screen quad (rectangle).

        The function is used to draw render results on.
        :param shader: The shader to use when rendering.
        """

        self._gl.glDisable(self._gl.GL_DEPTH_TEST)
        self._gl.glDisable(self._gl.GL_BLEND)

        shader.setUniformValue("u_modelViewProjectionMatrix", Matrix())

        if OpenGLContext.properties["supportsVertexArrayObjects"]:
            vao = QOpenGLVertexArrayObject()
            vao.create()
            vao.bind()

        self._quad_buffer.bind()

        shader.enableAttribute("a_vertex", "vector3f", 0)
        shader.enableAttribute("a_uvs", "vector2f", 72)

        self._gl.glDrawArrays(self._gl.GL_TRIANGLES, 0, 6)

        shader.disableAttribute("a_vertex")
        shader.disableAttribute("a_uvs")
        self._quad_buffer.release()

    def _initialize(self) -> None:
        supports_vao = OpenGLContext.supportsVertexArrayObjects()  # fill the OpenGLContext.properties
        Logger.log("d", "Support for Vertex Array Objects: %s", supports_vao)

        OpenGL()
        self._gl = OpenGL.getInstance().getBindingsObject()

        self._default_material = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "default.shader")) #type: ShaderProgram

        self.addRenderPass(DefaultPass(self._viewport_width, self._viewport_height))
        self.addRenderPass(SelectionPass(self._viewport_width, self._viewport_height))
        self.addRenderPass(CompositePass(self._viewport_width, self._viewport_height))

        buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        buffer.create()
        buffer.bind()
        buffer.allocate(120)
        data = numpy.array([
            -1.0, -1.0, 0.0,
             1.0,  1.0, 0.0,
            -1.0,  1.0, 0.0,
            -1.0, -1.0, 0.0,
             1.0, -1.0, 0.0,
             1.0,  1.0, 0.0,
             0.0,  0.0,
             1.0,  1.0,
             0.0,  1.0,
             0.0,  0.0,
             1.0,  0.0,
             1.0,  1.0
        ], dtype = numpy.float32).tostring()
        buffer.write(0, data, len(data))
        buffer.release()
        self._quad_buffer = buffer

        self._initialized = True
        self.initialized.emit()
