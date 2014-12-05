##  Abstract base class for tools that manipulate the scene.
#
class Tool(object):
    def __init__(self):
        super(Tool, self).__init__() # Call super to make multiple inheritence work.
        self._renderer = None

    ##  Handle an event.
    #   \param event \type{Event} The event to handle.
    #   \sa Event
    def event(self, event):
        pass

    ##  Return the name of the icon to use for this tool.
    def getIconName(self):
        return 'default.png'
