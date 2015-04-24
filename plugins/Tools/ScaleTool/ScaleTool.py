from UM.Tool import Tool
from UM.Event import Event, MouseEvent, KeyEvent
from UM.Application import Application
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection
from UM.Math.Plane import Plane
from UM.Math.Vector import Vector

from UM.Operations.ScaleOperation import ScaleOperation
from UM.Operations.GroupedOperation import GroupedOperation

from . import ScaleToolHandle

class ScaleTool(Tool):
    def __init__(self):
        super().__init__()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = ScaleToolHandle.ScaleToolHandle()

        self._lock_steps = True
        self._step_size = 0.05

        self._non_uniform_scale = False
        self._drag_length = 0

    def event(self, event):
        super().event(event)

        if event.type == Event.KeyPressEvent:
            if event.key == KeyEvent.ShiftKey:
                self._lock_steps = False
            elif event.key == KeyEvent.ControlKey:
                self._non_uniform_scale = True

        if event.type == Event.KeyReleaseEvent:
            if event.key == KeyEvent.ShiftKey:
                self._lock_steps = True
            elif event.key == KeyEvent.ControlKey:
                self._non_uniform_scale = False

        if event.type == Event.MousePressEvent:
            if MouseEvent.LeftButton not in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return False

            if ToolHandle.isAxis(id):
                self.setLockedAxis(id)

            handle_position = self._handle.getWorldPosition()

            if id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))
            elif id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector(0, 0, 1), handle_position.z))
            elif id == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))
            else:
                self.setDragPlane(Plane(Vector(0, 1, 0), handle_position.y))

            self.setDragStart(event.x, event.y)

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            handle_position = self._handle.getWorldPosition()
            drag_position = self.getDragPosition(event.x, event.y)
            if drag_position:
                drag_length = (drag_position - handle_position).length()
                if self._drag_length > 0:
                    drag_change = (drag_length - self._drag_length) / 100

                    if self._lock_steps and abs(drag_change) < self._step_size:
                        return False

                    scale = Vector(1.0, 1.0, 1.0)
                    if self._non_uniform_scale:
                        if self.getLockedAxis() == ToolHandle.XAxis:
                            scale.setX(1.0 + drag_change)
                        elif self.getLockedAxis() == ToolHandle.YAxis:
                            scale.setY(1.0 + drag_change)
                        elif self.getLockedAxis() == ToolHandle.ZAxis:
                            scale.setZ(1.0 + drag_change)

                    if scale == Vector(1.0, 1.0, 1.0):
                        scale.setX(1.0 + drag_change)
                        scale.setY(1.0 + drag_change)
                        scale.setZ(1.0 + drag_change)

                    Selection.applyOperation(ScaleOperation, scale)

                self._drag_length = (handle_position - drag_position).length()
                self.updateHandlePosition()
                return True

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(None)
                self._drag_length = 0
                return True
