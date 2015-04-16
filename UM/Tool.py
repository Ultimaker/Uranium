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

    def getLockedAxis(self):
        return self._locked_axis

    def setLockedAxis(self, axis):
        self._locked_axis = axis

        if self._handle:
            self._handle.setActiveAxis(axis)

    def getDragPlane(self):
        return self._drag_plane

    def setDragPlane(self, plane):
        self._drag_plane = plane

    def setDragStart(self, x, y):
        self._drag_start = self.getDragPosition(x, y)

    def getDragPosition(self, x, y):
        if not self._drag_plane:
            return None

        ray = self._controller.getScene().getActiveCamera().getRay(x, y)

        target = self._drag_plane.intersectsRay(ray)
        if target:
            return ray.getPointAlongRay(target)

        return None

    def getDragVector(self, x, y):
        if not self._drag_plane:
            return None

        if not self._drag_start:
            return None

        drag_end = self.getDragPosition(x, y)
        if drag_end:
            return drag_end - self._drag_start

        return None

