class Renderer(object):
    def __init__(self):
        super(Renderer, self).__init__()
        self._controller = None

    def renderMesh(self, position, mesh):
        pass

    def getController(self):
        return self._controller

    def setController(self, controller):
        self._controller = controller
