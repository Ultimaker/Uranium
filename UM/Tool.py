from UM.Signal import Signal, SignalEmitter
from UM.PluginObject import PluginObject
from UM.Event import Event
from UM.Scene.Selection import Selection

##  Abstract base class for tools that manipulate the scene.
#
class Tool(PluginObject, SignalEmitter):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritence work.
        self._controller = None
        self._handle = None
        self._locked_axis = None
        self._drag_plane = None
        self._drag_start = None

    ##  Handle an event.
    #   \param event \type{Event} The event to handle.
    #   \sa Event
    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            if Selection.hasSelection() and self._handle:
                self._handle.setParent(self.getController().getScene().getRoot())
                self._handle.setPosition(Selection.getAveragePosition())

        if event.type == Event.MouseMoveEvent and self._handle:
            if self._locked_axis:
                return

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                self._handle.setActiveAxis(None)

            if self._handle.isAxis(id):
                self._handle.setActiveAxis(id)

        if event.type == Event.ToolDeactivateEvent and self._handle:
            self._handle.setParent(None)

        return False

    def updateHandlePosition(self):
        if Selection.hasSelection():
            self._handle.setPosition(Selection.getAveragePosition())

    def getController(self):
        return self._controller

    def setController(self, controller):
        self._controller = controller

    def getHandle(self):
        return self._handle

    def setHandle(self, handle):
        self._handle = handle
