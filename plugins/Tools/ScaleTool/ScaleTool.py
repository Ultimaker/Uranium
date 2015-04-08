from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Application import Application
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection
from UM.Math.Plane import Plane
from UM.Math.Vector import Vector

from UM.Operations.ScaleOperation import ScaleOperation

from . import ScaleToolHandle

class ScaleTool(Tool):
    def __init__(self):
        super().__init__()
        self._renderer = Application.getInstance().getRenderer()
        self._handle = ScaleToolHandle.ScaleToolHandle()

        self._locked_axis = None
        self._drag = False
        self._target = None

        self._lock_steps = True
        self._step_size = 0.1

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            self._handle.setParent(self.getController().getScene().getRoot())
            self._handle.setPosition(Selection.getSelectedObject(0).getWorldPosition())

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

            handlePos = self._handle.getWorldPosition()
            plane = None
            if self._locked_axis == ToolHandle.XAxis:
                plane = Plane(Vector(0, 0, 1), handlePos.z)
            elif self._locked_axis == ToolHandle.YAxis:
                plane = Plane(Vector(0, 0, 1), handlePos.z)
            elif self._locked_axis == ToolHandle.ZAxis:
                plane = Plane(Vector(0, 1, 0), handlePos.y)

            if not plane:
                plane = Plane(Vector(0, 0, 1), handlePos.z)

            ray = camera.getRay(event.x, event.y)

            newTarget = plane.intersectsRay(ray)
            if newTarget:
                n = (handlePos - ray.getPointAlongRay(newTarget))
                if self._target:
                    diff = n - self._target
                    dist = -round(diff.length()) / 100

                    if abs(dist) < self._step_size:
                        return

                    scale = Vector(dist, dist, dist)

                    scale *= (diff.x / abs(diff.x))

                    #if self._locked_axis == ToolHandle.XAxis:
                        #scale.setX((diff.x / abs(diff.x)) * dist)
                    #elif self._locked_axis == ToolHandle.YAxis:
                        #scale.setY((diff.y / abs(diff.y)) * dist)
                    #elif self._locked_axis == ToolHandle.ZAxis:
                        #scale.setZ((diff.z / abs(diff.z)) * dist)
                    #else:
                        #scale.setData(dist, dist, dist)

                    for node in Selection.getAllSelectedObjects():
                        op = ScaleOperation(node, scale)
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
