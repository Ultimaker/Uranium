from PyQt5.QtGui import QColor, QOpenGLBuffer, QOpenGLContext, QOpenGLVersionProfile, QSurfaceFormat

from UM.Application import Application
from UM.View.Renderer import Renderer
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Resources import Resources
from UM.Logger import Logger

from . import QtGL2Material

import numpy
from ctypes import c_void_p

vertexBufferProperty = '__qtgl2_vertex_buffer'
indexBufferProperty = '__qtgl2_index_buffer'

##  A Renderer implementation using OpenGL2 to render.
class QtGL2Renderer(Renderer):
    def __init__(self):
        super().__init__()

        self._scene = Application.getInstance().getController().getScene()

        self._vertexBufferCache = {}
        self._indexBufferCache = {}

        self._initialized = False

        self._lightPosition = Vector(0, 0, 0)
        self._backgroundColor = QColor(128, 128, 128)
        self._viewportWidth = 0
        self._viewportHeight = 0

        self._solidsQueue = []
        self._transparentQueue = []
        self._overlayQueue = []

        self._camera = None

    def createMaterial(self, vert, frag):
        mat = QtGL2Material.QtGL2Material(self)
        mat.loadVertexShader(vert)
        mat.loadFragmentShader(frag)
        mat.build()
        return mat

    def setLightPosition(self, position):
        self._lightPosition = position

    def setBackgroundColor(self, color):
        self._backgroundColor = color

    def setViewportSize(self, width, height):
        self._viewportWidth = width
        self._viewportHeight = height

    def beginRendering(self):
        if not self._initialized:
            self._initialize()

        self._gl.glViewport(0, 0, self._viewportWidth, self._viewportHeight)
        self._gl.glClearColor(self._backgroundColor.redF(), self._backgroundColor.greenF(), self._backgroundColor.blueF(), self._backgroundColor.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

        if not QOpenGLContext.currentContext().format().renderableType() == QSurfaceFormat.OpenGLES:
            self._gl.glPointSize(2)

        self._solidsQueue.clear()
        self._transparentQueue.clear()
        self._overlayQueue.clear()

    def queueMesh(self, mesh, transform, **kwargs):
        queueItem = { 'transform': transform, 'mesh': mesh }

        queueItem['material'] = kwargs.get('material', self._defaultMaterial)

        mode = kwargs.get('mode', Renderer.RenderTriangles)
        if mode is Renderer.RenderLines:
            queueItem['mode'] = self._gl.GL_LINES
        elif mode is Renderer.RenderLineLoop:
            queueItem['mode'] = self._gl.GL_LINE_LOOP
        elif mode is Renderer.RenderPoints:
            queueItem['mode'] = self._gl.GL_POINTS
        else:
            queueItem['mode'] = self._gl.GL_TRIANGLES

        queueItem['wireframe'] = (mode == Renderer.RenderWireframe)

        if kwargs.get('transparent', False):
            self._transparentQueue.append(queueItem)
        elif kwargs.get('overlay', False):
            self._overlayQueue.append(queueItem)
        else:
            self._solidsQueue.append(queueItem)

    def renderQueuedMeshes(self):
        self._gl.glEnable(self._gl.GL_DEPTH_TEST)
        self._gl.glDepthFunc(self._gl.GL_LESS)
        self._gl.glDepthMask(self._gl.GL_TRUE)
        self._gl.glEnable(self._gl.GL_CULL_FACE)

        self._scene.acquireLock()

        self._camera = self._scene.getActiveCamera()
        if not self._camera:
            Logger.log("e", "No active camera set, can not render")
            self._scene.releaseLock()
            return

        for item in self._solidsQueue:
            self._renderItem(item)

        self._gl.glDepthMask(self._gl.GL_FALSE)
        self._gl.glEnable(self._gl.GL_BLEND)

        for item in self._transparentQueue:
            self._renderItem(item)

        self._gl.glDisable(self._gl.GL_DEPTH_TEST)

        for item in self._overlayQueue:
            self._renderItem(item)

        self._scene.releaseLock()

    def endRendering(self):
        pass

    def _initialize(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        self._gl.initializeOpenGLFunctions()

        self._defaultMaterial = QtGL2Material.QtGL2Material(self)
        self._defaultMaterial.loadVertexShader(Resources.getPath(Resources.ShadersLocation, 'default.vert'))
        self._defaultMaterial.loadFragmentShader(Resources.getPath(Resources.ShadersLocation, 'default.frag'))
        self._defaultMaterial.build()

        self._defaultMaterial.setUniformValue("u_ambientColor", [0.3, 0.3, 0.3, 1.0])
        self._defaultMaterial.setUniformValue("u_diffuseColor", [0.5, 0.5, 0.5, 1.0])
        self._defaultMaterial.setUniformValue("u_specularColor", [1.0, 1.0, 1.0, 1.0])
        self._defaultMaterial.setUniformValue("u_shininess", 50.0)

        self._initialized = True

    def _renderItem(self, item):
        mesh = item['mesh']
        transform = item['transform']
        material = item['material']
        mode = item['mode']
        wireframe = item.get('wireframe', False)

        material.bind()
        material.setUniformValue("u_projectionMatrix", self._camera.getProjectionMatrix(), cache = False)
        material.setUniformValue("u_viewMatrix", self._camera.getGlobalTransformation().getInverse(), cache = False)
        material.setUniformValue("u_viewPosition", self._camera.getGlobalPosition(), cache = False)
        material.setUniformValue("u_modelMatrix", transform, cache = False)
        material.setUniformValue("u_lightPosition", self._camera.getGlobalPosition(), cache = False)

        if mesh.hasNormals():
            normalMatrix = transform
            normalMatrix.setRow(3, [0, 0, 0, 1])
            normalMatrix.setColumn(3, [0, 0, 0, 1])
            normalMatrix = normalMatrix.getInverse().getTransposed()
            material.setUniformValue("u_normalMatrix", normalMatrix, cache = False)

        try:
            vertexBuffer = getattr(mesh, vertexBufferProperty)
        except AttributeError:
            vertexBuffer =  self._createVertexBuffer(mesh)
        vertexBuffer.bind()

        if mesh.hasIndices():
            try:
                indexBuffer = getattr(mesh, indexBufferProperty)
            except AttributeError:
                indexBuffer = self._createIndexBuffer(mesh)
            indexBuffer.bind()

        material.enableAttribute("a_vertex", Vector, 0)

        if mesh.hasNormals():
            material.enableAttribute("a_normal", Vector, mesh.getVertexCount() * 3 * 4)

        if wireframe:
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_LINE)

        if mesh.hasIndices():
            self._gl.glDrawElements(mode, mesh.getNumFaces() * 3 , self._gl.GL_UNSIGNED_INT, None)
        else:
            self._gl.glDrawArrays(mode, 0, mesh.getVertexCount())

        if wireframe:
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_FILL)

        material.disableAttribute("a_vertex")
        material.disableAttribute("a_normal")
        vertexBuffer.release()

        if mesh.hasIndices():
            indexBuffer.release()

        material.release()

    def _createVertexBuffer(self, mesh):
        buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        buffer.create()
        buffer.bind()
        vertices = mesh.getVerticesAsByteArray()

        if mesh.hasNormals():
            normals = mesh.getNormalsAsByteArray()
            ##Number of vertices * number of components (3 for vertex, 3 for normal) * size of 32-bit float (4)
            buffer.allocate(mesh.getVertexCount() * 6 * 4)
            buffer.write(0, vertices, len(vertices))
            buffer.write(len(vertices), normals, len(normals))
        else:
            buffer.allocate(vertices, mesh.getVertexCount() * 3 * 4)
        buffer.release()

        setattr(mesh, vertexBufferProperty, buffer)
        return buffer

    def _createIndexBuffer(self, mesh):
        buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        buffer.create()
        buffer.bind()

        data = mesh.getIndicesAsByteArray()
        buffer.allocate(data, len(data))
        buffer.release()

        setattr(mesh, indexBufferProperty, buffer)
        return buffer

