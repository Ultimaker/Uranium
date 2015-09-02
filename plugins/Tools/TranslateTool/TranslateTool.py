# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent, KeyEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.TranslateOperation import TranslateOperation
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import TranslateToolHandle

class TranslateTool(Tool):
    def __init__(self):
        super().__init__()

        self._renderer = Application.getInstance().getRenderer()
        self._handle = TranslateToolHandle.TranslateToolHandle()
        self._enabled_axis = [ToolHandle.XAxis, ToolHandle.YAxis, ToolHandle.ZAxis]

        self._grid_snap = False
        self._grid_size = 10

    def setEnabledAxis(self, axis):
        self._enabled_axis = axis
        self._handle.setEnabledAxis(axis)

    def event(self, event):
        super().event(event)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            self._grid_snap = True

        if event.type == Event.KeyReleaseEvent and event.key == KeyEvent.ShiftKey:
            self._grid_snap = False

        if event.type == Event.MousePressEvent:
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return False

            if id in self._enabled_axis:
                self.setLockedAxis(id)
            elif self._handle.isAxis(id):
                return False
            self.operationStarted.emit(self)
            if id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), 0))
            elif id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), 0))
            elif id == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector(0, 1, 0), 0))
            else:
                self.setDragPlane(Plane(Vector(0, 1, 0), 0))

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            if not self.getDragStart():
                self.setDragStart(event.x, event.y)
                return False

            drag = self.getDragVector(event.x, event.y)
            if drag:
                if self._grid_snap and drag.length() < self._grid_size:
                    return False

                if self.getLockedAxis() == ToolHandle.XAxis:
                    drag.setY(0)
                    drag.setZ(0)
                elif self.getLockedAxis() == ToolHandle.YAxis:
                    drag.setX(0)
                    drag.setZ(0)
                elif self.getLockedAxis() == ToolHandle.ZAxis:
                    drag.setX(0)
                    drag.setY(0)

                Selection.applyOperation(TranslateOperation, drag)

            self.setDragStart(event.x, event.y)
            return True

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                self.setLockedAxis(None)
                self.setDragPlane(None)
                self.setDragStart(None, None)
                self.operationStopped.emit(self)
                return True

        return False
