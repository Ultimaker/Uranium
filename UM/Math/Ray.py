# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Vector import Vector


class Ray:
    def __init__(self, origin: Vector = Vector(), direction: Vector = Vector()) -> None:
        self._origin = origin
        self._direction = direction
        self._inverse_direction = 1.0 / direction

    @property
    def origin(self) -> Vector:
        return self._origin

    @property
    def direction(self) -> Vector:
        return self._direction

    @property
    def inverseDirection(self) -> Vector:
        return self._inverse_direction

    def getPointAlongRay(self, distance: float) -> Vector:
        return self._origin + (self._direction * distance)

    def __repr__(self):
        return "Ray(origin = {0}, direction = {1})".format(self._origin, self._direction)
