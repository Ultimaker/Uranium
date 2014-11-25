from Cura.View.Renderer import Renderer

from OpenGL import GL

from Cura.View.GL2.Buffer import Buffer
from Cura.View.GL2.Shader import Shader

from Cura.Math.Matrix import Matrix

##  A Renderer implementation using OpenGL2 to render.
class GL2Renderer(Renderer):
    def __init__(self):
        super(Renderer, self).__init__()

        self._bufferCache = {}

        self._initialized = False

    def initialize(self):
        self._defaultShader = Shader()

        self._defaultShader.setVertexSource("""
            uniform mat4 modelMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 projectionMatrix;

            attribute vec4 vertex;

            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vertex;
            }
        """)
        self._defaultShader.setFragmentSource("""
            void main()
            {
                gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0);
            }
        """)
        self._defaultShader.build()

        self._initialized = True

    def renderMesh(self, position, mesh):
        if not self._initialized:
            self.initialize()

        if mesh not in self._bufferCache:
            vertexBuffer = Buffer(GL.GL_ARRAY_BUFFER, GL.GL_STATIC_DRAW)
            vertexBuffer.create(mesh.getVerticesList())
            self._bufferCache[mesh] = vertexBuffer

        self._defaultShader.bind()
        camera = self.getController().getScene().getActiveCamera()
        if camera:
            self._defaultShader.setUniform("projectionMatrix", camera.getProjectionMatrix())
            self._defaultShader.setUniform("viewMatrix", camera.getGlobalTransformation())
        else:
            self._defaultShader.setUniform("projectionMatrix", Matrix())
            self._defaultShader.setUniform("viewMatrix", Matrix())
        self._defaultShader.setUniform("modelMatrix", position)

        buffer = self._bufferCache[mesh]
        buffer.bind()
        self._defaultShader.bindAttribute("vertex", 3, GL.GL_FLOAT, 0)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, mesh.getNumVertices())
        self._defaultShader.releaseAttribute("vertex")
        buffer.release()
        self._defaultShader.release()
