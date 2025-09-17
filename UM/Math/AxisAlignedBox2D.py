# Copyright (c) 2025 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Float import Float

import numpy

from typing import Optional, Tuple, Union


class AxisAlignedBox2D:
    """Axis aligned 2D bounding box."""

    def __init__(self, minimum: numpy.ndarray, maximum: numpy.ndarray) -> None:
        self._min = numpy.array([min(minimum[0], maximum[0]), min(minimum[1], maximum[1])])
        self._max = numpy.array([max(minimum[0], maximum[0]), max(minimum[1], maximum[1])])

    def __iadd__(self, other: object) -> "AxisAlignedBox2D":
        if other is None or not isinstance(other, AxisAlignedBox2D) or not other.isValid():
            return self

        self._min = numpy.array([min(self._min[0], other._min[0]), min(self._min[1], other._min[1])])
        self._max = numpy.array([max(self._max[0], other._max[0]), max(self._max[1], other._max[1])])
        return self

    @property
    def width(self) -> float:
        return self._max[0] - self._min[0]

    @property
    def height(self) -> float:
        return self._max[1] - self._min[1]

    @property
    def left(self) -> float:
        return self._min[0]

    @property
    def right(self) -> float:
        return self._max[0]

    @property
    def bottom(self) -> float:
        return self._min[1]

    @property
    def top(self) -> float:
        return self._max[1]

    def isValid(self) -> bool:
        """Check if the bounding box is valid.
        Uses fuzzycompare to validate.
        :sa Float::fuzzyCompare()
        """

        return not(Float.fuzzyCompare(self._min[0], self._max[0]) or
                   Float.fuzzyCompare(self._min[1], self._max[1]))

    def __repr__(self) -> str:
        return "AxisAlignedBox2D(min = {0}, max = {1})".format(self._min, self._max)
