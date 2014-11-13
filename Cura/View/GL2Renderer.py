from Cura.View.Renderer import Renderer

from OpenGL import GL

class GL2Renderer(Renderer):
    def __init__(self):
        super(Renderer, self).__init__()

    def renderMesh(self, position, mesh):
        pass
