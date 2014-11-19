from Cura.View.GL2Renderer import GL2Renderer

## Abstract base class for view objects.
class View(object):
    def __init__(self):
        super(View, self).__init__()
        self._renderer = GL2Renderer()
        self._controller = None

    def getController(self):
        return self._controller

    def getRenderer(self):
        return self._renderer

    def setController(self, controller):
        self._controller = controller
        self._renderer.setController(controller)

    def render(self, glcontext):
        pass
