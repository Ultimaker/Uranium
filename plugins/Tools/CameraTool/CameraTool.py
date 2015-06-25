# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Application import Application

import math

class CameraTool(Tool):
    def __init__(self):
        super().__init__()
        self._scene = Application.getInstance().getController().getScene()

        self._yaw = 0
        self._pitch = 0
        self._origin = Vector(0, 0, 0)
        self._min_zoom = 10.0
        self._max_zoom = 1000.0

        self._rotate = False
        self._move = False
        self._dragged = False

        self._start_drag = None

        self._drag_distance = 0.05

    def setZoomRange(self, min, max):
        self._min_zoom = min
        self._max_zoom = max

    def setOrigin(self, origin):
        translation = origin - self._origin
        self._origin = origin
        self._scene.getActiveCamera().translate(translation)
        self._rotateCamera(0.0, 0.0)

    def getOrigin(self):
        return self._origin

    def event(self, event):
        if event.type is Event.MousePressEvent:
            if MouseEvent.RightButton in event.buttons:
                self._rotate = True
                self._start_drag = (event.x, event.y)
                return True
            elif MouseEvent.MiddleButton in event.buttons:
                self._move = True
                self._start_drag = (event.x, event.y)
                return True
        elif event.type is Event.MouseMoveEvent:
            if self._rotate or self._move:
                diff = (event.x - self._start_drag[0], event.y - self._start_drag[1])
                length_squared = diff[0] * diff[0] + diff[1] * diff[1]

                if length_squared > (self._drag_distance * self._drag_distance):
                    if self._rotate:
                        self._rotateCamera(event.deltaX, event.deltaY)
                        self._dragged = True
                        return True
                    elif self._move:
                        self._moveCamera(event)
                        self._dragged = True
                        return True
        elif event.type is Event.MouseReleaseEvent:
            if self._rotate or self._move:
                self._rotate = False
                self._move = False
                self._start_drag = None
            if self._dragged:
                self._dragged = False
                return True
        elif event.type is Event.MouseWheelEvent:
            self._zoomCamera(event)
            return True

        return False

    #   Moves the camera in response to a mouse event.
    def _moveCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera or not camera.isEnabled():
            return

        self._scene.acquireLock()

        camera_position = camera.getWorldPosition()
        camera.translate(Vector(-event.deltaX * 100, event.deltaY * 100, 0))
        translation = camera.getWorldPosition() - camera_position
        self._origin += translation

        self._scene.releaseLock()

    #   Zooms the camera in response to a mouse event.
    def _zoomCamera(self, event):
        camera = self._scene.getActiveCamera()
        if not camera or not camera.isEnabled():
            return

        self._scene.acquireLock()

        r = (camera.getWorldPosition() - self._origin).length()
        delta = r * (event.vertical / 128 / 10.0)
        r -= delta
        if delta > 0:
            if r > self._min_zoom:
                camera.translate(Vector(0.0, 0.0, -delta))
        else:
            if r < self._max_zoom:
                camera.translate(Vector(0.0, 0.0, -delta))

        self._scene.releaseLock()


    #   Rotates the camera in response to a mouse event.
    def _rotateCamera(self, x, y):
        camera = self._scene.getActiveCamera()
        if not camera or not camera.isEnabled():
            return

        self._scene.acquireLock()

        dx = math.radians(x * 180.0)
        dy = math.radians(y * 180.0)

        diff = camera.getPosition() - self._origin

        my = Matrix()
        my.setByRotationAxis(dx, Vector.Unit_Y)

        mx = Matrix(my.getData())
        mx.rotateByAxis(dy, Vector.Unit_Y.cross(diff).normalize())

        n = diff.multiply(mx)

        try:
            angle = math.acos(Vector.Unit_Y.dot(n.getNormalized()))
        except ValueError:
            return

        if angle < 0.1 or angle > math.pi - 0.1:
            n = diff.multiply(my)

        n += self._origin

        camera.setPosition(n)
        camera.lookAt(self._origin)

        self._scene.releaseLock()
