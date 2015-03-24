from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Application import Application
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion
from UM.Math.Float import Float

from UM.Operations.RotateOperation import RotateOperation

from . import RotateToolHandle

import math

class RotateTool(Tool):
    def __init__(self):
        super().__init__()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = RotateToolHandle.RotateToolHandle()

        self._locked_axis = None
        self._drag = False
        self._target = None

        self._step_size = 0.25

        self._x_rotate_step = Quaternion()
        self._x_rotate_step.setByAngleAxis(math.radians(15), Vector.Unit_X)

        self._y_rotate_step = Quaternion()
        self._y_rotate_step.setByAngleAxis(math.radians(15), Vector.Unit_Y)

        self._z_rotate_step = Quaternion()
        self._z_rotate_step.setByAngleAxis(math.radians(15), Vector.Unit_Z)

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            self._handle.setParent(self.getController().getScene().getRoot())
            self._handle.setPosition(Selection.getSelectedObject(0).getGlobalPosition())

        if event.type == Event.MousePressEvent:
            if not MouseEvent.LeftButton in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not id:
                return

            if ToolHandle.isAxis(id):
                self._locked_axis = id
                self._drag = True

        if event.type == Event.MouseMoveEvent:
            id = self._renderer.getIdAtCoordinate(event.x, event.y)
            if not self._locked_axis:
                if not id:
                    self._handle.setActiveAxis(None)

                if ToolHandle.isAxis(id):
                    self._handle.setActiveAxis(id)

            if not self._drag:
                return False

            camera = self.getController().getScene().getActiveCamera()

            handlePos = self._handle.getGlobalPosition()
            plane = None
            if self._locked_axis == ToolHandle.XAxis:
                plane = Plane(Vector(0, 0, 1), handlePos.z)
            elif self._locked_axis == ToolHandle.YAxis:
                plane = Plane(Vector(0, 0, 1), handlePos.z)
            elif self._locked_axis == ToolHandle.ZAxis:
                plane = Plane(Vector(0, 1, 0), handlePos.y)

            ray = camera.getRay(event.x, event.y)

            newTarget = plane.intersectsRay(ray)
            if newTarget:
                n = (handlePos - ray.getPointAlongRay(newTarget))
                if self._target:
                    diff = n - self._target

                    rotation = diff.length() / 100
                    if rotation < self._step_size:
                        return

                    newRotation = None
                    if self._locked_axis == ToolHandle.XAxis:
                        direction = diff.x / abs(diff.x)
                        newRotation = self._x_rotate_step if direction < 0 else self._x_rotate_step.getInverse()
                    elif self._locked_axis == ToolHandle.YAxis:
                        direction = diff.y / abs(diff.y)
                        newRotation = self._y_rotate_step if direction > 0 else self._y_rotate_step.getInverse()
                    elif self._locked_axis == ToolHandle.ZAxis:
                        direction = diff.z / abs(diff.z)
                        newRotation = self._z_rotate_step if direction > 0 else self._z_rotate_step.getInverse()

                    for node in Selection.getAllSelectedObjects():
                        op = RotateOperation(node, newRotation)
                        Application.getInstance().getOperationStack().push(op)

                self._target = n
            return True

        if event.type == Event.MouseReleaseEvent:
            if self._drag:
                self._target = None
                self._drag = False
                self._locked_axis = None
                return True

        if event.type == Event.ToolDeactivateEvent:
            self._handle.setParent(None)
