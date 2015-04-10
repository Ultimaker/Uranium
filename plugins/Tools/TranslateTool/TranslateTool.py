from UM.Tool import Tool
from UM.Event import Event, MouseEvent

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.TranslateOperation import TranslateOperation
from UM.Application import Application

from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from . import TranslateToolHandle

class TranslateTool(Tool):
    def __init__(self):
        super().__init__()

        self._renderer = Application.getInstance().getRenderer()

        self._handle = TranslateToolHandle.TranslateToolHandle()

        self._object = None
        self._target = None
        self._drag = False
        self._locked_axis = None

        self._previous_x = None
        self._previous_y = None

        self._min_x = float('-inf')
        self._max_x = float('inf')
        self._min_y = float('-inf')
        self._max_y = float('inf')
        self._min_z = float('-inf')
        self._max_z = float('inf')

        self._enabled_axis = [ToolHandle.XAxis, ToolHandle.YAxis, ToolHandle.ZAxis]

    def setEnabledAxis(self, axis):
        self._enabled_axis = axis

    def setXRange(self, min, max):
        self._min_x = min
        self._max_x = max

    def setYRange(self, min, max):
        self._min_y = min
        self._max_y = max

    def setZRange(self, min, max):
        self._min_z = min
        self._max_z = max

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            if Selection.hasSelection():
                #TODO: Support multiple selection
                self._handle.setParent(self.getController().getScene().getRoot())
                self._handle.setPosition(Selection.getSelectedObject(0).getWorldPosition())

        if event.type == Event.MousePressEvent:
            if not MouseEvent.LeftButton in event.buttons:
                return False

            id = self._renderer.getIdAtCoordinate(event.x, event.y, 5)
            if not id:
                return False

            if id in self._enabled_axis:
                self._locked_axis = id

            self._drag = True

        if event.type == Event.MouseMoveEvent:
            id = self._renderer.getIdAtCoordinate(event.x, event.y, 5)
            if not self._locked_axis:
                if not id:
                    self._handle.setActiveAxis(None)

                if id in self._enabled_axis:
                    self._handle.setActiveAxis(id)

            if not self._drag:
                return False

            camera = self.getController().getScene().getActiveCamera()

            plane = None
            if self._locked_axis == ToolHandle.XAxis:
                plane = Plane(Vector(0, 0, 1), 0)
            elif self._locked_axis == ToolHandle.YAxis:
                plane = Plane(Vector(0, 0, 1), 0)
            elif self._locked_axis == ToolHandle.ZAxis:
                plane = Plane(Vector(0, 1, 0), 0)

            if not plane:
                plane = Plane(Vector(0, 1, 0), 0)

            ray = camera.getRay(event.x, event.y)

            newTarget = plane.intersectsRay(ray)
            if newTarget:
                n = ray.getPointAlongRay(newTarget)
                if self._target:
                    diff = n - self._target

                    if self._locked_axis == ToolHandle.XAxis:
                        diff.setY(0)
                        diff.setZ(0)
                    elif self._locked_axis == ToolHandle.YAxis:
                        diff.setX(0)
                        diff.setZ(0)
                    elif self._locked_axis == ToolHandle.ZAxis:
                        diff.setX(0)
                        diff.setY(0)

                    position = Vector()
                    for node in Selection.getAllSelectedObjects():
                        op = TranslateOperation(node, diff)
                        Application.getInstance().getOperationStack().push(op)

                        position += node.getWorldPosition()

                    self._handle.setPosition(position / Selection.getCount())

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

        return False
