from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QOpenGLBuffer, QMatrix4x4, QOpenGLContext, QOpenGLVersionProfile

from Cura.View.Renderer import Renderer
from Cura.Math.Matrix import Matrix

import numpy

##  A Renderer implementation using OpenGL2 to render.
class QtGL2Renderer(Renderer):
    def __init__(self, application):
        super().__init__(application)

        self._bufferCache = {}

        self._initialized = False

    def initialize(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(2, 0)
        self._gl = QOpenGLContext.currentContext().versionFunctions(profile)
        self._gl.initializeOpenGLFunctions()

        vertexShader = QOpenGLShader(QOpenGLShader.Vertex)
        vertexShader.compileSourceCode("""
            uniform mat4 modelMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 projectionMatrix;

            attribute vec4 vertex;

            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vertex;
            }
        """)

        fragmentShader = QOpenGLShader(QOpenGLShader.Fragment)
        fragmentShader.compileSourceCode("""
            void main()
            {
                gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0);
            }
        """)

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

        if mesh not in self._bufferCache:
            vertexBuffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
            vertexBuffer.create()
            vertexBuffer.bind()
            vertexBuffer.allocate(mesh.getVerticesAsByteArray(), mesh.getNumVertices() * 12)
            vertexBuffer.release()
            self._bufferCache[mesh] = vertexBuffer

        self._defaultShader.bind()
        camera = self.getApplication().getController().getScene().getActiveCamera()
        if camera:
            self._defaultShader.setUniformValue("projectionMatrix", self._matrixToQMatrix4x4(camera.getProjectionMatrix()))
            self._defaultShader.setUniformValue("viewMatrix", self._matrixToQMatrix4x4(camera.getGlobalTransformation()))
        else:
            self._defaultShader.setUniformValue("projectionMatrix", QMatrix4x4())
            self._defaultShader.setUniformValue("viewMatrix", QMatrix4x4())
        self._defaultShader.setUniformValue("modelMatrix", self._matrixToQMatrix4x4(position))

        buffer = self._bufferCache[mesh]
        buffer.bind()

        self._defaultShader.setAttributeBuffer("vertex", self._gl.GL_FLOAT, 0, 3)
        self._defaultShader.enableAttributeArray("vertex")

        type = self._gl.GL_TRIANGLES
        if mode is Renderer.RenderLines:
            type = self._gl.GL_LINES
        elif mode is Renderer.RenderPoints:
            type = self._gl.GL_POINTS

        self._gl.glDrawArrays(type, 0, mesh.getNumVertices())
        
        self._defaultShader.disableAttributeArray("vertex")
        buffer.release()
        self._defaultShader.release()

    def clear(self, color):
        if not self._initialized:
            self.initialize()

        self._gl.glClearColor(color.redF(), color.greenF(), color.blueF(), color.alphaF())
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)

    ## private:

    # Get a transposed QMatrix4x4 out of a Cura Matrix
    def _matrixToQMatrix4x4(self, m):
        return QMatrix4x4(m.at(0,0), m.at(0, 1), m.at(0, 2), m.at(0, 3),
                          m.at(1,0), m.at(1, 1), m.at(1, 2), m.at(1, 3),
                          m.at(2,0), m.at(2, 1), m.at(2, 2), m.at(2, 3),
                          m.at(3,0), m.at(3, 1), m.at(3, 2), m.at(3, 3))


