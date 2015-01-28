from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Application import Application

import math

class CameraTool(Tool):
    def __init__(self, name):
        super().__init__(name)
        self._scene = Application.getInstance().getController().getScene()

        self._yaw = 0
        self._pitch = 0
        self._zoom = 5.0
        self._origin = Vector(0, 0, 0)
        self._minZoom = 10.0
        self._maxZoom = 300.0

    def setZoomRange(self, min, max):
        self._minZoom = min
        self._maxZoom = max

    def setOrigin(self, origin):
        translation = origin - self._origin
        self._origin = origin
        self._scene.getActiveCamera().translate(translation)
        self._rotateCamera(0.0, 0.0)

    def event(self, event):
        if type(event) is MouseEvent:
            if MouseEvent.RightButton in event.buttons:
                self._rotateCamera(event.deltaX, event.deltaY)
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

        self._scene.lock()

        camera.translate(Vector(event.deltaX / 100.0, event.deltaY / 100.0, 0))

        self._scene.unlock()

    #   Zooms the camera in response to a mouse event.
    def _zoomCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        self._scene.lock()

        delta = event.vertical / 10.0
        r = (camera.getGlobalPosition() - self._origin).length() - delta
        if delta > 0:
            if r > self._minZoom:
                camera.translate(Vector(0.0, 0.0, -delta))
        else:
            if r < self._maxZoom:
                camera.translate(Vector(0.0, 0.0, -delta))

        self._scene.unlock()


    #   Rotates the camera in response to a mouse event.
    def _rotateCamera(self, x, y):
        camera = self._scene.getActiveCamera()
        if not camera:
            return

        if camera.isLocked():
            return

        self._scene.lock()

        dx = x
        dy = y

        diff = camera.getGlobalPosition() - self._origin
        r = diff.length()

        m = Matrix()
        m.setByRotationAxis(dx, Vector.Unit_Y)
        m.rotateByAxis(dy, Vector.Unit_Y.cross(diff).normalize())

        n = diff.multiply(m)
        n += self._origin

        camera.setPosition(n)
        camera.lookAt(self._origin, Vector(0, 1, 0))

        self._scene.unlock()
