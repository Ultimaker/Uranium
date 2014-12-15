from UM.View.Renderer import Renderer

from OpenGL.GL import *

##  A Renderer subclass using classic (1.0-style) OpenGL to render.
class ClassicGLRenderer(Renderer):
    def __init__(self):
        super(Renderer, self).__init__()

    def renderMesh(self, position, mesh):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glLoadMatrixd(position.getData())

        glBegin(GL_TRIANGLES)
        vertex_count = mesh.getNumVerts()
        for index in range(vertex_count):
            vertex = mesh.getVertex(index)

            position = vertex.getPosition()
            glVertex3f(position.x, position.y, position.z)
            normal = vertex.getNormal()
            glNormal3f(normal.x, normal.y, normal.z)

        glEnd()

        glPopMatrix()
