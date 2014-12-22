from UM.Tool import Tool
from UM.Event import Event

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Float import Float

from UM.Operations.TranslateOperation import TranslateOperation
from UM.Application import Application

from UM.Scene.Selection import Selection

from . import TranslateToolHandle

class TranslateTool(Tool):
    def __init__(self, name):
        super().__init__(name)
        self._handle = TranslateToolHandle.TranslateToolHandle()

        self._object = None
        self._dragPlane = Plane(Vector.Unit_Y, 0.0)
        self._target = None

        self._min_x = float('-inf')
        self._max_x = float('inf')
        self._min_y = float('-inf')
        self._max_y = float('inf')
        self._min_z = float('-inf')
        self._max_z = float('inf')

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
            if Selection.getCount() > 0:
                #TODO: Support multiple selection
                self._handle.setParent(self.getController().getScene().getRoot())
                self._handle.setPosition(Selection.getSelectedObject(0).getGlobalPosition())

        if event.type == Event.MousePressEvent:
            #TODO: Support selection of multiple objects
            if Selection.getCount() > 0:
                obj = Selection.getSelectedObject(0)
                ray = self.getController().getScene().getActiveCamera().getRay(event.x, event.y)
                if obj.getBoundingBox().intersectsRay(ray):
                    self._object = obj
                    self._handle.setPosition(self._object.getGlobalPosition())

                    target = self._dragPlane.intersectsRay(ray)
                    if target:
                        self._target = ray.getPointAlongRay(target)

                    self.beginOperation.emit()

                    return True
                else:
                    return False

        if event.type == Event.MouseMoveEvent:
            #TODO: Make this more generic instead of assuming movement on a certain plane
            if self._object:
                ray = self.getController().getScene().getActiveCamera().getRay(event.x, event.y)

                newTarget = self._dragPlane.intersectsRay(ray)
                if newTarget:
                    n = ray.getPointAlongRay(newTarget)
                    if self._target:
                        t = n - self._target

                        #TODO: Use resulting world position instead of translation amount for clamping
                        t.setX(Float.clamp(t.x, self._min_x, self._max_x))
                        t.setY(Float.clamp(t.y, self._min_y, self._max_y))
                        t.setZ(Float.clamp(t.z, self._min_z, self._max_z))

                        op = TranslateOperation(self._object, t)
                        Application.getInstance().getOperationStack().push(op)

                        self._handle.setPosition(self._object.getGlobalPosition())

                    self._target = n
                return True

        if event.type == Event.MouseReleaseEvent:
            self._object = None
            self._target = None
            self.endOperation.emit()

        if event.type == Event.ToolDeactivateEvent:
            self._handle.setParent(None)

    def getIconName(self):
        return 'scale.png'
