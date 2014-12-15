## Abstract base class for view objects.
class View(object):
    def __init__(self):
        super(View, self).__init__()
        self._renderer = None
        self._controller = None

    ##  Get the controller object associated with this View.
    def getController(self):
        return self._controller

    ##  Set the controller object associated with this View.
    #   \param controller The controller object to use.
    def setController(self, controller):
        self._controller = controller

    ##  Get the Renderer instance for this View.
    def getRenderer(self):
        return self._renderer

    ##  Set the renderer object to use with this View.
    #   \param renderer \type{Renderer} The renderer to use.
    def setRenderer(self, renderer):
        self._renderer = renderer

    ##  Render the view.
    #   This method should be reimplemented by subclasses to perform the actual rendering.
    #   It is assumed there is an active, cleared OpenGL context when this method is called.
    def render(self):
        raise NotImplementedError("Views must implement the render() method")
