from PyQt5.QtGui import QOpenGLBuffer, QOpenGLContext, QOpenGLVersionProfile

from UM.View.Renderer import Renderer
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Resources import Resources
from UM.Logger import Logger

from . import QtGL2Material

import numpy
from ctypes import c_void_p

##  A Renderer implementation using OpenGL2 to render.
class QtGL2Renderer(Renderer):
    def __init__(self, application):
        super().__init__(application)

        self._vertexBufferCache = {}
        self._indexBufferCache = {}

        self._initialized = False
        self._lightPosition = Vector(0, 0, 0)

    def initialize(self):
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

    def setLightPosition(self, position):
        self._lightPosition = position

    def renderLines(self, position, mesh):
        if not self._initialized:
            self.initialize()

        if mesh not in self._vertexBufferCache:
            vertexBuffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
            vertexBuffer.create()
            vertexBuffer.bind()
            data = mesh.getVerticesAsByteArray()
            vertexBuffer.allocate(data, len(data))
            vertexBuffer.release()
            self._vertexBufferCache[mesh] = vertexBuffer

        camera = self.getApplication().getController().getScene().getActiveCamera()
        if not camera:
            Logger.log("e", "No active camera set, can not render")
            return

        self._defaultMaterial.bind()

        self._defaultMaterial.setUniformValue("u_projectionMatrix", camera.getProjectionMatrix(), cache = False)
        self._defaultMaterial.setUniformValue("u_viewMatrix", camera.getGlobalTransformation().getInverse(), cache = False)
        self._defaultMaterial.setUniformValue("u_viewPosition", camera.getGlobalPosition(), cache = False)
        self._defaultMaterial.setUniformValue("u_modelMatrix", position, cache = False)
        self._defaultMaterial.setUniformValue("u_lightPosition", self._lightPosition, cache = False)

        normalMatrix = position
        normalMatrix.setRow(3, [0, 0, 0, 1])
        normalMatrix.setColumn(3, [0, 0, 0, 1])
        normalMatrix = normalMatrix.getInverse().getTransposed()
        self._defaultMaterial.setUniformValue("u_normalMatrix", normalMatrix, cache = False)

        vertexBuffer = self._vertexBufferCache[mesh]
        vertexBuffer.bind()

        self._defaultMaterial.enableAttribute("a_vertex", Vector, 0)

        self._gl.glDrawArrays(self._gl.GL_LINES, 0, mesh.getVertexCount())

        self._defaultMaterial.disableAttribute("a_vertex")
        vertexBuffer.release()
        self._defaultMaterial.release()

    def renderMesh(self, position, mesh, **kwargs):
        if not self._initialized:
            self.initialize()

        mode = Renderer.RenderTriangles
        if 'mode' in kwargs:
            mode = kwargs['mode']

        material = self._defaultMaterial
        if 'material' in kwargs:
            material = kwargs['material']

        if mesh not in self._vertexBufferCache:
            vertexBuffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
            vertexBuffer.create()
            vertexBuffer.bind()
            vertices = mesh.getVerticesAsByteArray()

            if mesh.hasNormals():
                normals = mesh.getNormalsAsByteArray()
                #Number of vertices * number of components (3 for vertex, 3 for normal) * size of 32-bit float (4)
                vertexBuffer.allocate(mesh.getVertexCount() * 6 * 4)
                vertexBuffer.write(0, vertices, len(vertices))
                vertexBuffer.write(len(vertices), normals, len(normals))
            else:
                vertexBuffer.allocate(vertices, mesh.getVertexCount() * 3 * 4)

            vertexBuffer.release()
            self._vertexBufferCache[mesh] = vertexBuffer

            if mesh.hasIndices():
                index_buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
                index_buffer.create()
                index_buffer.bind()

                data = mesh.getIndicesAsByteArray()
                index_buffer.allocate(data, len(data))
                index_buffer.release()
                self._indexBufferCache[mesh] = index_buffer

        camera = self.getApplication().getController().getScene().getActiveCamera()
        if not camera:
            Logger.log("e", "No active camera set, can not render")
            return

        material.bind()

        material.setUniformValue("u_projectionMatrix", camera.getProjectionMatrix(), cache = False)
        material.setUniformValue("u_viewMatrix", camera.getGlobalTransformation().getInverse(), cache = False)
        material.setUniformValue("u_viewPosition", camera.getGlobalPosition(), cache = False)
        material.setUniformValue("u_modelMatrix", position, cache = False)
        material.setUniformValue("u_lightPosition", self._lightPosition, cache = False)

        normalMatrix = position
        normalMatrix.setRow(3, [0, 0, 0, 1])
        normalMatrix.setColumn(3, [0, 0, 0, 1])
        normalMatrix = normalMatrix.getInverse().getTransposed()
        material.setUniformValue("u_normalMatrix", normalMatrix, cache = False)

        vertexBuffer = self._vertexBufferCache[mesh]
        vertexBuffer.bind()

        if mesh.hasIndices():
            indexBuffer = self._indexBufferCache[mesh]
            indexBuffer.bind()

        material.enableAttribute("a_vertex", Vector, 0)

        if mesh.hasNormals():
            material.enableAttribute("a_normal", Vector, mesh.getVertexCount() * 3 * 4)

        type = self._gl.GL_TRIANGLES
        if mode is Renderer.RenderLines:
            type = self._gl.GL_LINES
        elif mode is Renderer.RenderPoints:
            type = self._gl.GL_POINTS
        elif mode is Renderer.RenderWireframe:
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_LINE)

        if mesh.hasIndices():
            self._gl.glDrawElements(type, mesh.getVertexCount(), self._gl.GL_UNSIGNED_INT, None)
        else:
            self._gl.glDrawArrays(type, 0, mesh.getVertexCount())

        if mode is Renderer.RenderWireframe:
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_FILL)

        material.disableAttribute("a_vertex")
        material.disableAttribute("a_normal")
        vertexBuffer.release()

        if mesh.hasIndices():
            indexBuffer.release()

        material.release()

    def preRender(self, size, color):
        if not self._initialized:
            self.initialize()

        self._gl.glViewport(0, 0, size.width(), size.height())
        self._gl.glClearColor(color.redF(), color.greenF(), color.blueF(), color.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

        self._gl.glEnable(self._gl.GL_DEPTH_TEST)
        self._gl.glDepthFunc(self._gl.GL_LESS)
        self._gl.glDepthMask(self._gl.GL_TRUE)
        self._gl.glEnable(self._gl.GL_CULL_FACE)
        self._gl.glPointSize(2)

    def createMaterial(self, vert, frag):
        mat = QtGL2Material.QtGL2Material(self)
        mat.loadVertexShader(vert)
        mat.loadFragmentShader(frag)
        mat.build()
        return mat
