##  Abstract base class for tools that manipulate the scene.
#
class Tool(object):
    def __init__(self, name):
        super(Tool, self).__init__() # Call super to make multiple inheritence work.
        self._name = name
        self._renderer = None
        self._controller = None

    ##  Get the name of this tool.
    def getName(self):
        return self._name

    ##  Handle an event.
    #   \param event \type{Event} The event to handle.
    #   \sa Event
    def event(self, event):
        pass

    def getController(self):
        return self._controller

    def setController(self, controller):
        self._controller = controller
