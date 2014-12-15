from UM.Math.Vector import Vector

class Ray:
    def __init__(self, origin = Vector(), direction = Vector()):
        self._origin = origin
        self._direction = direction
        self._invDirection = 1.0 / direction

    @property
    def origin(self):
        return self._origin

    @property
    def direction(self):
        return self._direction

    @property
    def inverseDirection(self):
        return self._invDirection
