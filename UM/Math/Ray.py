# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Math.Vector import Vector


class Ray:
    def __init__(self, origin = Vector(), direction = Vector()):
        self._origin = origin
        self._direction = direction
        self._inverse_direction = 1.0 / direction

    @property
    def origin(self):
        return self._origin

    @property
    def direction(self):
        return self._direction

    @property
    def inverseDirection(self):
        return self._inverse_direction

    def getPointAlongRay(self, distance):
        return self._origin + (self._direction * distance)

    def __repr__(self):
        return "Ray(origin = {0}, direction = {1})".format(self._origin, self._direction)
