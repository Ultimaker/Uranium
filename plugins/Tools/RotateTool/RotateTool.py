from UM.Tool import Tool
from UM.Event import Event, MouseEvent, KeyEvent
from UM.Application import Application
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion
from UM.Math.Float import Float

from UM.Operations.RotateOperation import RotateOperation
from UM.Operations.GroupedOperation import GroupedOperation

from . import RotateToolHandle

import math

class RotateTool(Tool):
    def __init__(self):
        super().__init__()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = RotateToolHandle.RotateToolHandle()

        self._lock_steps = True
        self._step_size = math.radians(15)

    def event(self, event):
        super().event(event)

        if event.type == Event.KeyPressEvent and event.key == KeyEvent.ShiftKey:
            self._lock_steps = False

        if event.type == Event.KeyReleaseEvent and event.key == KeyEvent.ShiftKey:
            self._lock_steps = True

        if event.type == Event.MousePressEvent:
            if not MouseEvent.LeftButton in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return

            if ToolHandle.isAxis(id):
                self.setLockedAxis(id)
                handle_position = self._handle.getWorldPosition()

                if id == ToolHandle.XAxis:
                    self.setDragPlane(Plane(Vector(1, 0, 0), handle_position.x))
                elif id == ToolHandle.YAxis:
                    self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))
                elif self._locked_axis == ToolHandle.ZAxis:
                    self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))

                self.setDragStart(event.x, event.y)

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            handle_position = self._handle.getWorldPosition()
            drag_start = (self.getDragStart() - handle_position).normalize()
            drag_position = self.getDragPosition(event.x, event.y)
            if not drag_position:
                return
            drag_end = (drag_position - handle_position).normalize()

            angle = math.acos(drag_start.dot(drag_end))
            if angle < self._step_size:
                return

            rotation = None
            if self.getLockedAxis() == ToolHandle.XAxis:
                direction = 1 if Vector.Unit_X.dot(drag_start.cross(drag_end)) > 0 else -1
                rotation = Quaternion.fromAngleAxis(direction * angle, Vector.Unit_X)
            elif self.getLockedAxis() == ToolHandle.YAxis:
                direction = 1 if Vector.Unit_Y.dot(drag_start.cross(drag_end)) > 0 else -1
                rotation = Quaternion.fromAngleAxis(direction * angle, Vector.Unit_Y)
            elif self.getLockedAxis() == ToolHandle.ZAxis:
                direction = 1 if Vector.Unit_Z.dot(drag_start.cross(drag_end)) > 0 else -1
                rotation = Quaternion.fromAngleAxis(direction * angle, Vector.Unit_Z)

            Selection.applyOperation(RotateOperation, rotation)

            self.setDragStart(event.x, event.y)
            self.updateHandlePosition()

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(None)
                return True

