# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, SignalEmitter
from UM.PluginObject import PluginObject
from UM.Event import Event
from UM.Scene.Selection import Selection
import UM.Application # Circular dependency blah

##  Abstract base class for tools that manipulate the scene.
#
class Tool(PluginObject, SignalEmitter):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritence work.
        self._controller = UM.Application.Application.getInstance().getController() # Circular dependency blah
        self._handle = None
        self._locked_axis = None
        self._drag_plane = None
        self._drag_start = None
        self._exposed_properties = []

    ##  Should be emitted whenever a longer running operation is started, like a drag to scale an object.
    #
    #   \param tool The tool that started the operation.
    operationStarted = Signal()
    ## Should be emitted whenever a longer running operation is stopped.
    #
    #   \param tool The tool that stopped the operation.
    operationStopped = Signal()

    propertyChanged = Signal()

    def getExposedProperties(self):
        return self._exposed_properties

    def setExposedProperties(self, *args):
        self._exposed_properties = args

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
    
    ##  Update the position of the ToolHandle
    #   \sa ToolHandle
    def updateHandlePosition(self):
        if Selection.hasSelection():
            self._handle.setPosition(Selection.getAveragePosition())
    
    ##  Convenience function 
    def getController(self):
        return self._controller
    
    ##  Get the associated handle 
    #   \return \type{ToolHandle}
    def getHandle(self):
        return self._handle
    
    ##  set the associated handle 
    #   \param \type{ToolHandle}
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

    def getDragStart(self):
        return self._drag_start

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
