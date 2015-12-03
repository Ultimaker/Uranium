# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QColor, QOpenGLBuffer, QOpenGLContext, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat, QSurfaceFormat, QOpenGLVersionProfile, QImage

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.Selection import Selection
from UM.Scene.PointCloudNode import PointCloudNode
from UM.Math.Color import Color

from UM.Mesh.MeshBuilder import MeshBuilder
from UM.View.CompositePass import CompositePass
from UM.View.DefaultPass import DefaultPass
from UM.View.SelectionPass import SelectionPass
from UM.View.GL.OpenGL import OpenGL
from UM.View.RenderBatch import RenderBatch
from UM.Qt.GL.QtOpenGL import QtOpenGL

import numpy
import copy
from ctypes import c_void_p

vertexBufferProperty = "__qtgl2_vertex_buffer"
indexBufferProperty = "__qtgl2_index_buffer"

##  A Renderer implementation using OpenGL2 to render.
class QtRenderer(Renderer):
    def __init__(self):
        super().__init__()

        self._controller = Application.getInstance().getController()
        self._scene = self._controller.getScene()

        self._vertex_buffer_cache = {}
        self._index_buffer_cache = {}

        self._initialized = False

        self._light_position = Vector(0, 0, 0)
        self._background_color = QColor(128, 128, 128)
        self._viewport_width = 0
        self._viewport_height = 0
        self._window_width = 0
        self._window_height = 0

        self._batches = []

        self._quad_buffer = None

        self._camera = None

    def getPixelMultiplier(self):
        # Standard assumption for screen pixel density is 96 DPI. We use that as baseline to get
        # a multiplication factor we can use for screens > 96 DPI.
        return round(Application.getInstance().primaryScreen().physicalDotsPerInch() / 96.0)

    def getBatches(self):
        return self._batches

    def addRenderPass(self, render_pass):
        super().addRenderPass(render_pass)
        render_pass.setSize(self._viewport_width, self._viewport_height)

    ##  Set background color of the rendering.
    def setBackgroundColor(self, color):
        self._background_color = color

    def setViewportSize(self, width, height):
        self._viewport_width = width
        self._viewport_height = height

        for render_pass in self._render_passes:
            render_pass.setSize(width, height)

    def setWindowSize(self, width, height):
        self._window_width = width
        self._window_height = height

    def getWindowSize(self):
        return (self._window_width, self._window_height)

    def beginRendering(self):
        if not self._initialized:
            self._initialize()

        self._gl.glViewport(0, 0, self._viewport_width, self._viewport_height)
        self._gl.glClearColor(self._background_color.redF(), self._background_color.greenF(), self._background_color.blueF(), self._background_color.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
        self._gl.glClearColor(0.0, 0.0, 0.0, 0.0)

    ##  Put a node in the render queue
    def queueNode(self, node, **kwargs):
        type = RenderBatch.RenderType.Solid
        if kwargs.get("transparent", False):
            type = RenderBatch.RenderType.Transparent
        elif kwargs.get("overlay", False):
            type = RenderBatch.RenderType.Overlay

        batch = RenderBatch(
            type = type,
            mode = kwargs.get("mode", RenderBatch.RenderMode.Triangles),
            shader = kwargs.get("shader", self._default_material),
            backface_cull = kwargs.get("backface_cull", True),
            range = kwargs.get("range", None)
        )

        batch.addItem(node.getWorldTransformation(), kwargs.get("mesh", node.getMeshData()))

        self._batches.append(batch)
    
    ##  Render all nodes in the queue
    def renderQueuedNodes(self):
        self._batches.sort()

        for render_pass in self.getRenderPasses():
            render_pass.render()

    def endRendering(self):
        self._batches.clear()

    def renderFullScreenQuad(self, shader):
        self._gl.glDisable(self._gl.GL_DEPTH_TEST)
        self._gl.glDisable(self._gl.GL_BLEND)

        shader.setUniformValue("u_modelViewProjectionMatrix", Matrix())

        self._quad_buffer.bind()

        shader.enableAttribute("a_vertex", "vector3f", 0)
        shader.enableAttribute("a_uvs", "vector2f", 72)

        self._gl.glDrawArrays(self._gl.GL_TRIANGLES, 0, 6)

        shader.disableAttribute("a_vertex")
        shader.disableAttribute("a_uvs")
        self._quad_buffer.release()

    def _initialize(self):
        OpenGL.setInstance(QtOpenGL())
        self._gl = OpenGL.getInstance().getBindingsObject()

        self._default_material = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "default.shader"))

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
