# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Vector import Vector
from UM.Math.Float import Float


class Plane:
    """Plane representation using normal and distance."""

    def __init__(self, normal = Vector(), distance = 0.0):
        super().__init__()

        self._normal = normal
        self._distance = distance

    @property
    def normal(self):
        return self._normal

    @property
    def distance(self):
        return self._distance

    def intersectsRay(self, ray):
        w = ray.origin - (self._normal * self._distance)

        nDotR = self._normal.dot(ray.direction)
        nDotW = -self._normal.dot(w)

        if Float.fuzzyCompare(nDotR, 0.0):
            return False

        t = nDotW / nDotR
        if t < 0:
            return False

        return t

    def __repr__(self):
        return "Plane(normal = {0}, distance = {1})".format(self._normal, self._distance)
