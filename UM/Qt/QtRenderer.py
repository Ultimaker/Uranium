# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import numpy
from PyQt5.QtGui import QColor, QOpenGLBuffer, QOpenGLVertexArrayObject
from typing import List, Optional, Tuple

from UM.Application import Application
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
    from UM.Controller import Controller
    from UM.Scene.Scene import Scene
    from UM.Scene.Camera import Camera
    from UM.Scene.SceneNode import SceneNode
    from UM.View.RenderPass import RenderPass
    from UM.View.GL.ShaderProgram import ShaderProgram


vertexBufferProperty = "__qtgl2_vertex_buffer"
indexBufferProperty = "__qtgl2_index_buffer"


##  A Renderer implementation using PyQt's OpenGL implementation to render.
@signalemitter
class QtRenderer(Renderer):
    def __init__(self) -> None:
        super().__init__()

        self._controller = Application.getInstance().getController()  # type: Controller
        self._scene = self._controller.getScene()  # type: Scene

        self._initialized = False  # type: bool

        self._light_position = Vector(0, 0, 0)  # type: Vector
        self._background_color = QColor(128, 128, 128)  # type: QColor
        self._viewport_width = 0  # type: int
        self._viewport_height = 0  # type: int
        self._window_width = 0  # type: int
        self._window_height = 0  # type: int

        self._batches = []  # type: List[RenderBatch]

        self._quad_buffer = None  # type: QOpenGLBuffer

        self._camera = None  # type: Optional[Camera]

    initialized = Signal()

    ##  Get an integer multiplier that can be used to correct for screen DPI.
    def getPixelMultiplier(self) -> int:
        # Standard assumption for screen pixel density is 96 DPI. We use that as baseline to get
        # a multiplication factor we can use for screens > 96 DPI.
        return round(UM.Qt.QtApplication.QtApplication.getInstance().primaryScreen().physicalDotsPerInch() / 96.0)

    ##  Get the list of render batches.
    def getBatches(self) -> List[RenderBatch]:
        return self._batches

    ##  Overridden from Renderer.
    #
    #   This makes sure the added render pass has the right size.
    def addRenderPass(self, render_pass: "RenderPass") -> None:
        super().addRenderPass(render_pass)
        render_pass.setSize(self._viewport_width, self._viewport_height)

    ##  Set background color used when rendering.
    def setBackgroundColor(self, color: QColor) -> None:
        self._background_color = color

    def getViewportWidth(self) -> int:
        return self._viewport_width

    def getViewportHeight(self) -> int:
        return self._viewport_height

    ##  Set the viewport size.
    #
    #   \param width The new width of the viewport.
    #   \param height The new height of the viewport.
    def setViewportSize(self, width: int, height: int) -> None:
        self._viewport_width = width
        self._viewport_height = height

        for render_pass in self._render_passes:
            render_pass.setSize(width, height)

    ##  Set the window size.
    def setWindowSize(self, width: int, height: int) -> None:
        self._window_width = width
        self._window_height = height

    ##  Get the window size.
    #
    #   \return A tuple of (window_width, window_height)
    def getWindowSize(self) -> Tuple[int, int]:
        return self._window_width, self._window_height

    ##  Overrides Renderer::beginRendering()
    def beginRendering(self) -> None:
        if not self._initialized:
            self._initialize()

        self._gl.glViewport(0, 0, self._viewport_width, self._viewport_height)
        self._gl.glClearColor(self._background_color.redF(), self._background_color.greenF(), self._background_color.blueF(), self._background_color.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
        self._gl.glClearColor(0.0, 0.0, 0.0, 0.0)

    ##  Overrides Renderer::queueNode()
    def queueNode(self, node: "SceneNode", **kwargs) -> None:
        type = kwargs.pop("type", RenderBatch.RenderType.Solid)
        if kwargs.pop("transparent", False):
            type = RenderBatch.RenderType.Transparent
        elif kwargs.pop("overlay", False):
            type = RenderBatch.RenderType.Overlay

        shader = kwargs.pop("shader", self._default_material)
        batch = RenderBatch(shader, type = type, **kwargs)

        batch.addItem(node.getWorldTransformation(), kwargs.get("mesh", node.getMeshData()), kwargs.pop("uniforms", None))

        self._batches.append(batch)

    ##  Overrides Renderer::render()
    def render(self) -> None:
        self._batches.sort()

        for render_pass in self.getRenderPasses():
            width, height = render_pass.getSize()
            self._gl.glViewport(0, 0, width, height)
            render_pass.render()

    ##  Sometimes not an *entire* new render is required (QML is updated, but the scene did not).
    #   In that case we ask the composite pass (which must be the last render pass) to render (instead of re-rendering
    #   all the passes & the views.
    def reRenderLast(self):
        self.beginRendering() # First ensure that the viewport is set correctly.
        self.getRenderPasses()[-1].render()

    ##  Overrides Renderer::endRendering()
    def endRendering(self) -> None:
        self._batches.clear()

    ##  Render a full screen quad (rectangle).
    #
    #   The function is used to draw render results on.
    #   \param shader The shader to use when rendering.
    def renderFullScreenQuad(self, shader: "ShaderProgram") -> None:
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

        self._render_passes.add(DefaultPass(self._viewport_width, self._viewport_height))
        self._render_passes.add(SelectionPass(self._viewport_width, self._viewport_height))
        self._render_passes.add(CompositePass(self._viewport_width, self._viewport_height))

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
