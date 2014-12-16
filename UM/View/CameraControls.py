from UM.Event import Event, MouseEvent
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix

from copy import deepcopy

import math

class CameraControls:
    def __init__(self, scene):
        self._scene = scene

        self._yaw = 0
        self._pitch = 0
        self._zoom = 5.0
        self._origin = Vector(0, 0, 0)
        self._minZoom = 5.0
        self._maxZoom = 250.0

    def event(self, event):
        if type(event) is MouseEvent:
            if MouseEvent.RightButton in event.buttons:
                self._rotateCamera(event)
                return True
            elif MouseEvent.MiddleButton in event.buttons:
                self._moveCamera(event)
                return True
        elif event.type is Event.MouseWheelEvent:
            self._zoomCamera(event)
            return True

        return False

    #   Moves the camera in response to a mouse event.
    def _moveCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        camera.translate(Vector(event.deltaX / 100.0, event.deltaY / 100.0, 0))

    #   Zooms the camera in response to a mouse event.
    def _zoomCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        delta = event.vertical / 10.0
        r = (camera.getGlobalPosition() - self._origin).length() - delta
        if r > self._minZoom and r < self._maxZoom:
            camera.translate(Vector(0.0, 0.0, -delta))


    #   Rotates the camera in response to a mouse event.
    def _rotateCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        dx = event.deltaX / 100.0 #TODO: Make this time based
        dy = event.deltaY / 100.0

        diff = camera.getGlobalPosition() - self._origin
        r = diff.length()

        m = Matrix()
        m.setByRotationAxis(dx, Vector.Unit_Y)
        m.rotateByAxis(dy, Vector.Unit_X)

        n = diff.rotated(m)
        n += self._origin

        # Limit the vertical rotation by calculating the dot product between the
        # new vector and the up vector then checking if that is within a certain
        # threshold. If not, perform the rotation only along the Y axis.
        d = n.getNormalized().dot(Vector.Unit_Y)
        if d < 0.05 or d > math.pi * 0.3:
            m.setByRotationAxis(dx, Vector.Unit_Y)
            n = diff.rotated(m)

        camera.setPosition(n)
        camera.lookAt(self._origin, Vector(0, 1, 0))
