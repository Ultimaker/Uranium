# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter
from UM.PluginObject import PluginObject
from UM.Event import Event
from UM.Scene.Selection import Selection
import UM.Application  # Circular dependency blah

from UM.Controller import Controller
from UM.Scene.ToolHandle import ToolHandle

from typing import Optional


##  Abstract base class for tools that manipulate (or otherwise interact with) the scene.
#
@signalemitter
class Tool(PluginObject):
    def __init__(self):
        super().__init__()
        self._controller = UM.Application.Application.getInstance().getController()  # Circular dependency blah
        self._enabled = True

        self._handle = None  # type: Optional[ToolHandle]
        self._locked_axis = None
        self._drag_plane = None
        self._drag_start = None
        self._exposed_properties = []

        self._selection_pass = None

        self._controller.toolEnabledChanged.connect(self._onToolEnabledChanged)
        self._shortcut_key = None

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

    def getShortcutKey(self):
        return self._shortcut_key

    ##  Handle an event.
    #   \param event \type{Event} The event to handle.
    #   \return \type{bool} true if this event has been handled and requires
    #           no further processing.
    #   \sa Event
    def event(self, event: Event) -> Optional[bool]:
        if not self._selection_pass:
            self._selection_pass = UM.Application.Application.getInstance().getRenderer().getRenderPass("selection")

        if event.type == Event.ToolActivateEvent:
            if Selection.hasSelection() and self._handle:
                self._handle.setParent(self.getController().getScene().getRoot())

        if event.type == Event.MouseMoveEvent and self._handle:
            if self._locked_axis:
                return

            tool_id = self._selection_pass.getIdAtPosition(event.x, event.y)

            if self._handle.isAxis(tool_id):
                self._handle.setActiveAxis(tool_id)
            else:
                self._handle.setActiveAxis(None)

        if event.type == Event.ToolDeactivateEvent and self._handle:
            self._handle.setParent(None)

        return False

    ##  Convenience function
    def getController(self) -> Controller:
        return self._controller

    ##  Get the enabled state of the tool
    def getEnabled(self) -> bool:
        return self._enabled

    ##  Get the associated handle
    #   \return \type{ToolHandle}
    def getHandle(self) -> Optional[ToolHandle]:
        return self._handle

    ##  set the associated handle
    #   \param \type{ToolHandle}
    def setHandle(self, handle: ToolHandle):
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

    def _onToolEnabledChanged(self, tool_id: str, enabled: bool):
        if tool_id == self._plugin_id:
            self._enabled = enabled
