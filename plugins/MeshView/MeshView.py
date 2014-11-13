from Cura.View.View import View

from OpenGL import GL

class MeshView(View):
    def __init__(self):
        super(MeshView, self).__init__()

    def render(self, glcontext):
        GL.glClearColor(1.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
