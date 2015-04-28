from UM.PluginObject import PluginObject


## Abstract base class for view objects.
class View(PluginObject):
    def __init__(self):
        super().__init__()
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

    ##  Begin the rendering process.
    #
    #   This should queue all the meshes that should be rendered.
    def beginRendering(self):
        raise NotImplementedError()

    ##  Perform any steps needed when ending the rendering process.
    #
    #   If there is any cleanup or other tasks that need to be performed
    #   after rendering this method should be used.
    def endRendering(self):
        raise NotImplementedError()
