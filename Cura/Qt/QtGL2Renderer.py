from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QOpenGLBuffer, QMatrix4x4, QOpenGLContext, QOpenGLVersionProfile, QVector3D, QColor

from Cura.View.Renderer import Renderer
from Cura.Math.Vector import Vector
from Cura.Math.Matrix import Matrix
from Cura.Resources import Resources
from Cura.Logger import Logger

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

        self._defaultShader = QOpenGLShaderProgram()
        self._defaultShader.addShaderFromSourceFile(QOpenGLShader.Vertex, Resources.getPath(Resources.ShadersLocation, 'default.vert'));
        self._defaultShader.addShaderFromSourceFile(QOpenGLShader.Fragment, Resources.getPath(Resources.ShadersLocation, 'default.frag'));
        self._defaultShader.link()

        #TODO: Use proper uniform location indices
        #self._defaultShader.bind()
        #self._projectionMatrixLocation = self._defaultShader.uniformLocation("projectionMatrix");
        #self._viewMatrixLocation = self._defaultShader.uniformLocation("viewMatrix");
        #self._modelMatrixLocation = self._defaultShader
        #self._defaultShader.release()

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

        if not self._defaultShader.isLinked():
            return
        self._defaultShader.bind()

        self._defaultShader.setUniformValue("u_projectionMatrix", self._matrixToQMatrix4x4(camera.getProjectionMatrix()))
        self._defaultShader.setUniformValue("u_viewMatrix", self._matrixToQMatrix4x4(camera.getGlobalTransformation().getInverse()))
        self._defaultShader.setUniformValue("u_viewPosition", self._vectorToQVector3D(camera.getGlobalPosition()))
        self._defaultShader.setUniformValue("u_modelMatrix", self._matrixToQMatrix4x4(position))

        normalMatrix = position
        normalMatrix.setRow(3, [0, 0, 0, 1])
        normalMatrix.setColumn(3, [0, 0, 0, 1])
        normalMatrix = normalMatrix.getInverse().getTransposed()
        self._defaultShader.setUniformValue("u_normalMatrix", self._matrixToQMatrix4x4(normalMatrix))

        self._defaultShader.setUniformValue("u_ambientColor", QColor(255, 0, 0))
        self._defaultShader.setUniformValue("u_diffuseColor", QColor(0, 0, 0))
        self._defaultShader.setUniformValue("u_specularColor", QColor(0, 0, 0))

        self._defaultShader.setUniformValue("u_lightPosition", self._vectorToQVector3D(self._lightPosition))
        self._defaultShader.setUniformValue("u_lightColor", QColor(255, 255, 255))

        self._defaultShader.setUniformValue("u_shininess", 50.0)

        vertexBuffer = self._vertexBufferCache[mesh]
        vertexBuffer.bind()

        self._defaultShader.setAttributeBuffer("a_vertex", self._gl.GL_FLOAT, 0, 3, 0)
        self._defaultShader.enableAttributeArray("a_vertex")

        self._gl.glDrawArrays(self._gl.GL_LINES, 0, mesh.getVertexCount())

        self._defaultShader.disableAttributeArray("a_vertex")
        vertexBuffer.release()
        self._defaultShader.release()

    def renderMesh(self, position, mesh, mode = Renderer.RenderTriangles):
        if not self._initialized:
            self.initialize()

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
                vertexBuffer.allocate(data, mesh.getVertexCount() * 3 * 4)

            vertexBuffer.release()
            self._vertexBufferCache[mesh] = vertexBuffer

            indexBuffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
            indexBuffer.create()
            indexBuffer.bind()
            data = mesh.getIndicesAsByteArray()
            indexBuffer.allocate(data, len(data))
            indexBuffer.release()
            self._indexBufferCache[mesh] = indexBuffer

        camera = self.getApplication().getController().getScene().getActiveCamera()
        if not camera:
            Logger.log("e", "No active camera set, can not render")
            return

        if not self._defaultShader.isLinked():
            return
        self._defaultShader.bind()

        self._defaultShader.setUniformValue("u_projectionMatrix", self._matrixToQMatrix4x4(camera.getProjectionMatrix()))
        self._defaultShader.setUniformValue("u_viewMatrix", self._matrixToQMatrix4x4(camera.getGlobalTransformation().getInverse()))
        self._defaultShader.setUniformValue("u_viewPosition", self._vectorToQVector3D(camera.getGlobalPosition()))
        self._defaultShader.setUniformValue("u_modelMatrix", self._matrixToQMatrix4x4(position))

        normalMatrix = position
        normalMatrix.setRow(3, [0, 0, 0, 1])
        normalMatrix.setColumn(3, [0, 0, 0, 1])
        normalMatrix = normalMatrix.getInverse().getTransposed()
        self._defaultShader.setUniformValue("u_normalMatrix", self._matrixToQMatrix4x4(normalMatrix))

        self._defaultShader.setUniformValue("u_ambientColor", QColor(80, 80, 80))
        self._defaultShader.setUniformValue("u_diffuseColor", QColor(128, 128, 128))
        self._defaultShader.setUniformValue("u_specularColor", QColor(255, 255, 255))

        self._defaultShader.setUniformValue("u_lightPosition", self._vectorToQVector3D(self._lightPosition))
        self._defaultShader.setUniformValue("u_lightColor", QColor(255, 255, 255))

        self._defaultShader.setUniformValue("u_shininess", 50.0)

        vertexBuffer = self._vertexBufferCache[mesh]
        vertexBuffer.bind()
        indexBuffer = self._indexBufferCache[mesh]
        indexBuffer.bind()

        self._defaultShader.setAttributeBuffer("a_vertex", self._gl.GL_FLOAT, 0, 3)
        self._defaultShader.enableAttributeArray("a_vertex")

        self._defaultShader.setAttributeBuffer("a_normal", self._gl.GL_FLOAT, mesh.getVertexCount() * 3 * 4, 3)
        self._defaultShader.enableAttributeArray("a_normal")

        type = self._gl.GL_TRIANGLES
        if mode is Renderer.RenderLines:
            type = self._gl.GL_LINES
        elif mode is Renderer.RenderPoints:
            type = self._gl.GL_POINTS
        elif mode is Renderer.RenderWireframe:
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_LINE)

        self._gl.glDrawElements(type, mesh.getVertexCount(), self._gl.GL_UNSIGNED_INT, None)

        if mode is Renderer.RenderWireframe:
            self._gl.glPolygonMode(self._gl.GL_FRONT_AND_BACK, self._gl.GL_FILL)

        self._defaultShader.disableAttributeArray("a_vertex")
        self._defaultShader.disableAttributeArray("a_normal")
        vertexBuffer.release()
        indexBuffer.release()
        self._defaultShader.release()

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

    ## private:

    # Get a transposed QMatrix4x4 out of a Cura Matrix
    def _matrixToQMatrix4x4(self, m):
        return QMatrix4x4(m.at(0,0), m.at(0, 1), m.at(0, 2), m.at(0, 3),
                          m.at(1,0), m.at(1, 1), m.at(1, 2), m.at(1, 3),
                          m.at(2,0), m.at(2, 1), m.at(2, 2), m.at(2, 3),
                          m.at(3,0), m.at(3, 1), m.at(3, 2), m.at(3, 3))

    def _vectorToQVector3D(self, v):
        return QVector3D(v.x, v.y, v.z)

    def setDepthTesting(self, depthTesting):
        if depthTesting:
            self._gl.glEnable(self._gl.GL_DEPTH_TEST)
        else:
            self._gl.glDisable(self._gl.GL_DEPTH_TEST)

