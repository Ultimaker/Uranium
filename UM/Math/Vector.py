# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import numpy
import numpy.linalg
import math
from UM.Math.Float import Float

from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.Math.Matrix import Matrix

# Disable divide-by-zero warnings so that 1.0 / (1.0, 0.0, 0.0) returns (1.0, Inf, Inf) without complaining
numpy.seterr(divide="ignore")


class Vector:
    """Simple 3D-vector class based on numpy arrays.

    This class represents an immutable 3-dimensional vector.
    """

    # These fields are filled in below. This is needed to help static analysis tools (read: PyCharm)
    Null = None     # type: Vector
    Unit_X = None   # type: Vector
    Unit_Y = None   # type: Vector
    Unit_Z = None   # type: Vector

    def __init__(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None, data: Optional[numpy.ndarray] = None, round_digits: Optional[int] = None) -> None:
        """Initialize a new vector
        :param x: X coordinate of vector.
        :param y: Y coordinate of vector.
        :param z: Z coordinate of vector.
        """

        if x is not None and y is not None and z is not None:
            self._data = numpy.array([x, y, z], dtype = numpy.float64)
        elif data is not None:
            self._data = data.copy()
        else:
            self._data = numpy.zeros(3, dtype = numpy.float64)
        self.round_digits = round_digits  # for comparisons

    def getData(self) -> numpy.ndarray:
        """Get numpy array with the data
        :returns: numpy array of length 3 holding xyz data.
        """

        return self._data.astype(numpy.float64)

    def setRoundDigits(self, digits: int) -> None:
        self.round_digits = digits

    @property
    def x(self):
        """Return the x component of this vector"""

        return numpy.float64(self._data[0])

    @property
    def y(self):
        """Return the y component of this vector"""

        return numpy.float64(self._data[1])

    @property
    def z(self):
        """Return the z component of this vector"""

        return numpy.float64(self._data[2])

    def set(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> "Vector":
        new_x = self._data[0] if x is None else x
        new_y = self._data[1] if y is None else y
        new_z = self._data[2] if z is None else z
        return Vector(new_x, new_y, new_z)

    def angleToVector(self, vector: "Vector") -> float:
        """Get the angle from this vector to another"""

        v0 = numpy.array(self._data, dtype = numpy.float64, copy = False)
        v1 = numpy.array(vector.getData(), dtype = numpy.float64, copy = False)
        dot = numpy.sum(v0 * v1)
        dot /= self._normalizeVector(v0) * self._normalizeVector(v1)
        return numpy.arccos(numpy.fabs(dot))

    def normalized(self) -> "Vector":
        l = self.length()
        if l != 0:
            new_data = self._data / l
            return Vector(data=new_data)
        else:
            return self

    def _normalizeVector(self, data: numpy.ndarray) -> numpy.ndarray:
        """Return length, i.e. Euclidean norm, of ndarray along axis."""

        data = numpy.array(data, dtype = numpy.float64, copy = True)
        if data.ndim == 1:
            return math.sqrt(numpy.dot(data, data))
        data *= data
        out = numpy.atleast_1d(numpy.sum(data))
        numpy.sqrt(out, out)
        return out

    def length(self) -> float:
        return numpy.linalg.norm(self._data)

    def dot(self, other) -> numpy.ndarray:
        return numpy.dot(self._data, other._data)

    def cross(self, other) -> "Vector":
        result = numpy.cross(self._data, other._data)
        return Vector(result[0], result[1], result[2])

    def multiply(self, matrix: "Matrix") -> "Vector":
        d = numpy.empty(4, dtype = numpy.float64)
        d[0] = self._data[0]
        d[1] = self._data[1]
        d[2] = self._data[2]
        d[3] = 1.0

        d = d.dot(matrix.getData())

        return Vector(d[0], d[1], d[2])

    def preMultiply(self, matrix: "Matrix") -> "Vector":
        d = numpy.empty(4, dtype = numpy.float64)
        d[0] = self._data[0]
        d[1] = self._data[1]
        d[2] = self._data[2]
        d[3] = 1.0

        d = matrix.getData().dot(d)

        return Vector(d[0], d[1], d[2])

    def scale(self, other: "Vector") -> "Vector":
        """Scale a vector by another vector.

        This will do a component-wise multiply of the two vectors.
        """

        return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

    def __eq__(self, other):
        if self is other:
            return True
        if other is None:
            return False
        return self.equals(other)

    def equals(self, other: "Vector", epsilon: float = 1e-6) -> bool:
        """Compares this vector to another vector.

        :param epsilon: optional tolerance value for the comparision.
        :returns: True if the two vectors are the same.
        """

        return Float.fuzzyCompare(self.x, other.x, epsilon) and \
               Float.fuzzyCompare(self.y, other.y, epsilon) and \
               Float.fuzzyCompare(self.z, other.z, epsilon)

    def __add__(self, other):
        if type(other) is Vector:
            return Vector(data = self._data + other._data)
        else:
            return Vector(data = self._data + other)

    def __iadd__(self, other):
        return self + other

    def __sub__(self, other):
        if type(other) is Vector:
            return Vector(data = self._data - other._data)
        else:
            return Vector(data = self._data - other)

    def __isub__(self, other):
        return self - other

    def __mul__(self, other):
        if isNumber(other):
            new_data = self._data * other
        elif type(other) is Vector:
            new_data = self._data * other._data
        else:
            raise NotImplementedError()
        return Vector(data=new_data)

    def __imul__(self, other):
        return self * other

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isNumber(other):
            new_data = self._data / other
        elif type(other) is Vector:
            new_data = self._data / other._data
        else:
            raise NotImplementedError()
        return Vector(data = new_data)

    def __itruediv__(self, other):
        return self / other

    def __rtruediv__(self, other):
        if isNumber(other):
            new_data = other / self._data
        elif type(other) is Vector:
            new_data = other._data / self._data
        else:
            raise NotImplementedError()
        return Vector(data=new_data)

    def __neg__(self):
        return Vector(data = -1 * self._data)

    def __repr__(self):
        return "Vector({0:.3}, {1:.3}, {2:.3})".format(self._data[0], self._data[1], self._data[2])

    def __str__(self):
        return "<{0:.3},{1:.3},{2:.3}>".format(self._data[0], self._data[1], self._data[2])

    def __lt__(self, other):
        return self._data[0] < other._data[0] and self._data[1] < other._data[1] and self._data[2] < other._data[2]

    def __gt__(self, other):
        return self._data[0] > other._data[0] and self._data[1] > other._data[1] and self._data[2] > other._data[2]

    def __le__(self, other):
        if self.round_digits is None:
            return self._data[0] <= other._data[0] and self._data[1] <= other._data[1] and self._data[2] <= other._data[2]
        else:
            return (
                round(self._data[0], self.round_digits) <= round(other._data[0], self.round_digits) and
                round(self._data[1], self.round_digits) <= round(other._data[1], self.round_digits) and
                round(self._data[2], self.round_digits) <= round(other._data[2], self.round_digits))

    def __ge__(self, other):
        if self.round_digits is None:
            return self._data[0] >= other._data[0] and self._data[1] >= other._data[1] and self._data[2] >= other._data[2]
        else:
            return (
                round(self._data[0], self.round_digits) >= round(other._data[0], self.round_digits) and
                round(self._data[1], self.round_digits) >= round(other._data[1], self.round_digits) and
                round(self._data[2], self.round_digits) >= round(other._data[2], self.round_digits))


def isNumber(value: Any) -> bool:
    return type(value) in [float, int, numpy.float32, numpy.float64]


Vector.Null = Vector()
Vector.Unit_X = Vector(1, 0, 0)
Vector.Unit_Y = Vector(0, 1, 0)
Vector.Unit_Z = Vector(0, 0, 1)
