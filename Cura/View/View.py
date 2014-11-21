from Cura.View.GL2Renderer import GL2Renderer

## Abstract base class for view objects.
class View(object):
    def __init__(self):
        super(View, self).__init__()
        self._renderer = GL2Renderer()
        self._controller = None

    ##  Get the controller object associated with this View.
    def getController(self):
        return self._controller

    ##  Get the Renderer instance for this View.
    def getRenderer(self):
        return self._renderer

    ##  Set the controller object associated with this View.
    #   \param controller The controller object to use.
    def setController(self, controller):
        self._controller = controller
        self._renderer.setController(controller)

    ##  Render the view.
    #   This method should be reimplemented by subclasses to perform the actual rendering.
    #   It is assumed there is an active, cleared OpenGL context when this method is called.
    def render(self):
        raise NotImplementedError("Views must implement the render() method")
