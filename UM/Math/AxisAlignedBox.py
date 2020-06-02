# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Float import Float
from UM.Math.Ray import Ray #For typing.
from UM.Math.Vector import Vector

import numpy

from typing import Optional, Tuple, Union


class AxisAlignedBox:
    """Axis aligned bounding box."""

    class IntersectionResult:
        NoIntersection = 1
        PartialIntersection = 2
        FullIntersection = 3

    def __init__(self, minimum: Vector = Vector.Null, maximum: Vector = Vector.Null) -> None:
        if minimum.x > maximum.x or minimum.y > maximum.y or minimum.z > maximum.z:
            swapped_minimum = Vector(min(minimum.x, maximum.x), min(minimum.y, maximum.y), min(minimum.z, maximum.z))
            swapped_maximum = Vector(max(minimum.x, maximum.x), max(minimum.y, maximum.y), max(minimum.z, maximum.z))
            minimum = swapped_minimum
            maximum = swapped_maximum
        minimum.setRoundDigits(3)
        maximum.setRoundDigits(3)
        self._min = minimum #type: Vector
        self._max = maximum #type: Vector

    def set(self, minimum: Optional[Vector] = None, maximum: Optional[Vector] = None, left: Optional[float] = None,
            right: Optional[float] = None, top: Optional[float] = None, bottom: Optional[float] = None,
            front: Optional[float] = None, back: Optional[float] = None) -> "AxisAlignedBox":
        if minimum is None:
            minimum = self._min

        if maximum is None:
            maximum = self._max

        if left is not None or bottom is not None or back is not None:
            left = minimum.x if left is None else left
            bottom = minimum.y if bottom is None else bottom
            back = minimum.z if back is None else back
            minimum = Vector(left, bottom, back)

        if right is not None or top is not None or front is not None:
            right = maximum.x if right is None else right
            top = maximum.y if top is None else top
            front = maximum.z if front is None else front
            maximum = Vector(right, top, front)

        return AxisAlignedBox(minimum, maximum)

    def __add__(self, other: object) -> "AxisAlignedBox":
        if other is None or not isinstance(other, AxisAlignedBox) or not other.isValid():
            return self

        new_min = Vector(min(self._min.x, other.left), min(self._min.y, other.bottom),
                         min(self._min.z, other.back))
        new_max = Vector(max(self._max.x, other.right), max(self._max.y, other.top),
                         max(self._max.z, other.front))
        return AxisAlignedBox(minimum=new_min, maximum=new_max)

    def __iadd__(self, other: object) -> "AxisAlignedBox":
        raise NotImplementedError()

    @property
    def width(self) -> float:
        return self._max.x - self._min.x

    @property
    def height(self) -> float:
        return self._max.y - self._min.y

    @property
    def depth(self) -> float:
        return self._max.z - self._min.z

    @property
    def center(self) -> Vector:
        return self._min + ((self._max - self._min) / 2.0)

    @property
    def left(self) -> float:
        return self._min.x

    @property
    def right(self) -> float:
        return self._max.x

    @property
    def bottom(self) -> float:
        return self._min.y

    @property
    def top(self) -> float:
        return self._max.y

    @property
    def back(self) -> float:
        return self._min.z

    @property
    def front(self) -> float:
        return self._max.z

    @property
    def minimum(self) -> Vector:
        return self._min

    @property
    def maximum(self) -> Vector:
        return self._max

    def isValid(self) -> bool:
        """Check if the bounding box is valid.
        Uses fuzzycompare to validate.
        :sa Float::fuzzyCompare()
        """

        return not(Float.fuzzyCompare(self._min.x, self._max.x) or
                   Float.fuzzyCompare(self._min.y, self._max.y) or
                   Float.fuzzyCompare(self._min.z, self._max.z))

    def intersectsRay(self, ray: Ray) -> Union[Tuple[float, float], bool]:
        """Intersect the bounding box with a ray
        :sa Ray
        """

        inv = ray.inverseDirection

        t = numpy.empty((2,3), dtype=numpy.float32)
        t[0, 0] = inv.x * (self._min.x - ray.origin.x)
        t[0, 1] = inv.y * (self._min.y - ray.origin.y)
        t[0, 2] = inv.z * (self._min.z - ray.origin.z)
        t[1, 0] = inv.x * (self._max.x - ray.origin.x)
        t[1, 1] = inv.y * (self._max.y - ray.origin.y)
        t[1, 2] = inv.z * (self._max.z - ray.origin.z)

        tmin = numpy.min(t, axis=0)
        tmax = numpy.max(t, axis=0)

        largest_min = numpy.max(tmin)
        smallest_max = numpy.min(tmax)

        if smallest_max > largest_min:
            return (largest_min, smallest_max)
        else:
            return False

    def intersectsBox(self, box: "AxisAlignedBox") -> int:
        """Check to see if this box intersects another box.

        :param box: The box to check for intersection.
        :return: NoIntersection when no intersection occurs, PartialIntersection when partially intersected, FullIntersection when box is fully contained inside this box.
        """

        if self._min.x > box._max.x or box._min.x > self._max.x:
            return self.IntersectionResult.NoIntersection

        if self._min.y > box._max.y or box._min.y > self._max.y:
            return self.IntersectionResult.NoIntersection

        if self._min.z > box._max.z or box._min.z > self._max.z:
            return self.IntersectionResult.NoIntersection

        if box._min >= self._min and box._max <= self._max:
            return self.IntersectionResult.FullIntersection

        return self.IntersectionResult.PartialIntersection

    def __repr__(self) -> str:
        return "AxisAlignedBox(min = {0}, max = {1})".format(self._min, self._max)

    # This field is filled in below. This is needed to help static analysis tools (read: PyCharm)
    Null = None  # type: AxisAlignedBox
AxisAlignedBox.Null = AxisAlignedBox()
