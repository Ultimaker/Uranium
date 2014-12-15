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

        self._yaw += dx
        if self._yaw > math.pi:
            self._yaw -= math.pi
        elif self._yaw < -math.pi:
            self._yaw += math.pi

        self._pitch += dy
        if self._pitch > math.pi:
            self._pitch -= math.pi
        elif self._pitch < -math.pi:
            self._pitch += math.pi

        diff = camera.getGlobalPosition() - self._origin
        r = diff.length()

        m = Matrix()
        m.setByRotationAxis(dy, Vector.Unit_X)
        m.rotateByAxis(dx, Vector.Unit_Y)

        n = diff.rotated(m)
        n += self._origin

        camera.setPosition(n)
        camera.lookAt(Vector(0, 0, 0), Vector(0, 1, 0))
