from UM.Tool import Tool
from UM.Event import Event

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector

from . import TranslateToolHandle

class TranslateTool(Tool):
    def __init__(self):
        super().__init__()
        self._handle = TranslateToolHandle.TranslateToolHandle()

        self._object = None
        self._dragPlane = Plane(Vector.Unit_Y, 0.0)

    def event(self, event):
        if event.type == Event.ToolActivateEvent:
            self._handle.setParent(self.getController().getScene().getRoot())

        if event.type == Event.MousePressEvent:
            #TODO: Add a proper selection class
            if self.getController()._selectionControls._selection:
                obj = self.getController()._selectionControls._selection[0]
                ray = self.getController().getScene().getActiveCamera().getRay(event.x, event.y)
                if obj.getBoundingBox().intersectsRay(ray):
                    self._object = obj
                    self._handle.setPosition(self._object.getGlobalPosition())

        if event.type == Event.MouseMoveEvent:
            if self._object:
                ray = self.getController().getScene().getActiveCamera().getRay(event.x, event.y)

                target = self._dragPlane.intersectsRay(ray)
                if target:
                    self._object.setPosition(ray.getPointAlongRay(target))
                    self._handle.setPosition(ray.getPointAlongRay(target))


        if event.type == Event.MouseReleaseEvent:
            self._object = None


        if event.type == Event.ToolDeactivateEvent:
            self._handle.setParent(None)

    def getIconName(self):
        return 'scale.png'
