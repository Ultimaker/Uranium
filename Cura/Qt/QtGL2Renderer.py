from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QOpenGLBuffer, QMatrix4x4, QOpenGLContext, QOpenGLVersionProfile, QVector3D, QColor

from Cura.View.Renderer import Renderer
from Cura.Math.Matrix import Matrix
from Cura.Resources import Resources

import numpy
from ctypes import c_void_p

##  A Renderer implementation using OpenGL2 to render.
class QtGL2Renderer(Renderer):
    def __init__(self, application):
        super().__init__(application)

        self._vertexBufferCache = {}
        self._indexBufferCache = {}

        self._initialized = False

    def initialize(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        self._gl.initializeOpenGLFunctions()

        vertexShader = QOpenGLShader(QOpenGLShader.Vertex)
        with open(Resources.locate(Resources.ResourcesLocation, "shaders", "default.vert")) as f:
            vertexShader.compileSourceCode(f.read())

        fragmentShader = QOpenGLShader(QOpenGLShader.Fragment)
        with open(Resources.locate(Resources.ResourcesLocation, "shaders", "default.frag")) as f:
            fragmentShader.compileSourceCode(f.read())

        self._defaultShader = QOpenGLShaderProgram()
        self._defaultShader.addShader(vertexShader);
        self._defaultShader.addShader(fragmentShader);
        self._defaultShader.link()

        #TODO: Use proper uniform location indices
        #self._defaultShader.bind()
        #self._projectionMatrixLocation = self._defaultShader.uniformLocation("projectionMatrix");
        #self._viewMatrixLocation = self._defaultShader.uniformLocation("viewMatrix");
        #self._modelMatrixLocation = self._defaultShader
        #self._defaultShader.release()

        self._initialized = True

    def renderMesh(self, position, mesh, mode = Renderer.RenderTriangles):
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

            indexBuffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
            indexBuffer.create()
            indexBuffer.bind()
            data = mesh.getIndicesAsByteArray()
            indexBuffer.allocate(data, len(data))
            indexBuffer.release()
            self._indexBufferCache[mesh] = indexBuffer

        self._defaultShader.bind()
        camera = self.getApplication().getController().getScene().getActiveCamera()
        if camera:
            self._defaultShader.setUniformValue("u_projectionMatrix", self._matrixToQMatrix4x4(camera.getProjectionMatrix()))
            self._defaultShader.setUniformValue("u_viewMatrix", self._matrixToQMatrix4x4(camera.getGlobalTransformation().getInverse()))
        else:
            self._defaultShader.setUniformValue("u_projectionMatrix", QMatrix4x4())
            self._defaultShader.setUniformValue("u_viewMatrix", QMatrix4x4())
        self._defaultShader.setUniformValue("u_modelMatrix", self._matrixToQMatrix4x4(position))

        self._defaultShader.setUniformValue("u_ambientColor", QColor(128, 128, 128))
        self._defaultShader.setUniformValue("u_diffuseColor", QColor(190, 190, 190))
        self._defaultShader.setUniformValue("u_specularColor", QColor(255, 255, 255))

        self._defaultShader.setUniformValue("u_lightPosition", QVector3D(0.0, 200.0, 200.0))
        self._defaultShader.setUniformValue("u_lightIntensity", 1.0)
        self._defaultShader.setUniformValue("u_lightColor", QColor(255, 255, 255))

        self._defaultShader.setUniformValue("u_viewPosition", QVector3D(0.0, 0.0, 200.0))

        self._defaultShader.setUniformValue("u_ambientFactor", 0.2)
        self._defaultShader.setUniformValue("u_diffuseFactor", 0.8)
        self._defaultShader.setUniformValue("u_specularFactor", 0.5)
        self._defaultShader.setUniformValue("u_specularStrength", 5.0)

        vertexBuffer = self._vertexBufferCache[mesh]
        vertexBuffer.bind()
        indexBuffer = self._indexBufferCache[mesh]
        indexBuffer.bind()

        self._defaultShader.setAttributeBuffer("a_vertex", self._gl.GL_FLOAT, 0, 3, 24)
        self._defaultShader.enableAttributeArray("a_vertex")

        self._defaultShader.setAttributeBuffer("a_normal", self._gl.GL_FLOAT, 12, 3, 24)
        self._defaultShader.enableAttributeArray("a_normal")

        type = self._gl.GL_TRIANGLES
        if mode is Renderer.RenderLines:
            type = self._gl.GL_LINES
        elif mode is Renderer.RenderPoints:
            type = self._gl.GL_POINTS

        self._gl.glDrawElements(type, mesh.getNumVertices(), self._gl.GL_UNSIGNED_INT, None)

        self._defaultShader.disableAttributeArray("a_vertex")
        self._defaultShader.disableAttributeArray("a_normal")
        vertexBuffer.release()
        indexBuffer.release()
        self._defaultShader.release()

    def clear(self, color):
        if not self._initialized:
            self.initialize()

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


