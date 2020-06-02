# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import numpy
import numpy.linalg
import math
import copy

from UM.Math.Vector import Vector
from UM.Math.Float import Float
from UM.Math.Matrix import Matrix

class Quaternion:
    """Unit Quaternion class based on numpy arrays.

    This class represents a Unit quaternion that can be used for rotations.

    :note The operations that modify this quaternion will ensure the length
    of the quaternion remains 1. This is done to make this class simpler
    to use.

    """

    EPS = numpy.finfo(float).eps * 4.0

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0) -> None:
        # Components are stored as XYZW
        self._data = numpy.array([x, y, z, w], dtype=numpy.float64)

    def getData(self):
        return self._data

    @property
    def x(self):
        return self._data[0]

    @property
    def y(self):
        return self._data[1]

    @property
    def z(self):
        return self._data[2]

    @property
    def w(self):
        return self._data[3]

    def setByAngleAxis(self, angle: float, axis: Vector) -> None:
        """Set quaternion by providing rotation about an axis.

        :param angle: :type{float} Angle in radians
        :param axis: :type{Vector} Axis of rotation
        """

        a = axis.normalized().getData()
        halfAngle = angle / 2.0
        self._data[3] = math.cos(halfAngle)
        self._data[0:3] = a * math.sin(halfAngle)
        self.normalize()

    def __mul__(self, other):
        result = copy.deepcopy(self)
        result *= other
        return result

    def __imul__(self, other):
        if type(other) is Quaternion:
            v1 = Vector(other.x, other.y, other.z)
            v2 = Vector(self.x, self.y, self.z)

            w = other.w * self.w - v1.dot(v2)
            v = v2 * other.w + v1 * self.w + v2.cross(v1)

            self._data[0] = v.x
            self._data[1] = v.y
            self._data[2] = v.z
            self._data[3] = w
        elif type(other) is float or type(other) is int:
            self._data *= other
        else:
            raise NotImplementedError()

        return self

    def __add__(self, other):
        result = copy.deepcopy(self)
        result += other
        return result

    def __iadd__(self, other):
        if type(other) is Quaternion:
            self._data[0] += other._data[0]
            self._data[1] += other._data[1]
            self._data[2] += other._data[2]
            self._data[3] += other._data[3]
        else:
            raise NotImplementedError()

        return self

    def __truediv__(self, other):
        result = copy.deepcopy(self)
        result /= other
        return result

    def __itruediv__(self, other):
        if type(other) is float or type(other) is int:
            self._data /= other
        else:
            raise NotImplementedError()

        return self

    def __eq__(self, other):
        return Float.fuzzyCompare(self.x, other.x, 1e-6) and Float.fuzzyCompare(self.y, other.y, 1e-6) and Float.fuzzyCompare(self.z, other.z, 1e-6) and Float.fuzzyCompare(self.w, other.w, 1e-6)

    def __neg__(self):
        q = copy.deepcopy(self)
        q._data = -q._data
        return q

    def getInverse(self) -> "Quaternion":
        result = copy.deepcopy(self)
        result.invert()
        return result

    def invert(self) -> "Quaternion":
        self._data[0:3] = -self._data[0:3]
        return self

    def rotate(self, vector):
        vMult = 2.0 * (self.x * vector.x + self.y * vector.y + self.z * vector.z)
        crossMult = 2.0 * self.w
        pMult = crossMult * self.w - 1.0

        return Vector( pMult * vector.x + vMult * self.x + crossMult * (self.y * vector.z - self.z * vector.y),
                       pMult * vector.y + vMult * self.y + crossMult * (self.z * vector.x - self.x * vector.z),
                       pMult * vector.z + vMult * self.z + crossMult * (self.x * vector.y - self.y * vector.x) )

    def dot(self, other):
        return numpy.dot(self._data, other._data)

    def length(self) -> float:
        return numpy.linalg.norm(self._data)

    def normalize(self) -> None:
        self._data /= numpy.linalg.norm(self._data)

    def setByMatrix(self, matrix: Matrix, ensure_unit_length: bool = False) -> None:
        """Set quaternion by providing a homogeneous (4x4) rotation matrix.

        :param matrix: 4x4 Matrix object
        :param ensure_unit_length:
        """

        trace = matrix.at(0, 0) + matrix.at(1, 1) + matrix.at(2, 2)
        if trace > 0.0:
            self._data[0] = matrix.at(2, 1) - matrix.at(1, 2)
            self._data[1] = matrix.at(0, 2) - matrix.at(2, 0)
            self._data[2] = matrix.at(1, 0) - matrix.at(0, 1)
            self._data[3] = trace + 1
        else:
            i = 0
            if matrix.at(1, 1) > matrix.at(0, 0):
                i = 1

            if matrix.at(2, 2) > matrix.at(i, i):
                i = 2

            # Yes, this is repeated code. Writing it out however makes the code way
            # more readable than any magical index shifting.
            if i == 0:
                self._data[0] = matrix.at(0, 0) - matrix.at(1, 1) - matrix.at(2, 2) + 1.0
                self._data[1] = matrix.at(0, 1) + matrix.at(1, 0)
                self._data[2] = matrix.at(0, 2) + matrix.at(2, 0)
                self._data[3] = matrix.at(2, 1) - matrix.at(1, 2)
            elif i == 1:
                self._data[0] = matrix.at(0, 1) + matrix.at(1, 0)
                self._data[1] = matrix.at(1, 1) - matrix.at(0, 0) - matrix.at(2, 2) + 1.0
                self._data[2] = matrix.at(1, 2) + matrix.at(2, 1)
                self._data[3] = matrix.at(0, 2) - matrix.at(2, 0)
            else:
                self._data[0] = matrix.at(0, 2) + matrix.at(2, 0)
                self._data[1] = matrix.at(2, 1) + matrix.at(1, 2)
                self._data[1] = matrix.at(2, 2) - matrix.at(0, 0) - matrix.at(1, 1) + 1.0
                self._data[3] = matrix.at(1, 0) - matrix.at(0, 1)
        if ensure_unit_length:
            self.normalize()

    def toMatrix(self) -> Matrix:
        m = numpy.zeros((4, 4), dtype=numpy.float64)

        s = 2.0 / (self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

        xs = s * self.x
        ys = s * self.y
        zs = s * self.z

        wx = self.w * xs
        wy = self.w * ys
        wz = self.w * zs

        xx = self.x * xs
        xy = self.x * ys
        xz = self.x * zs

        yy = self.y * ys
        yz = self.y * zs
        zz = self.z * zs

        m[0, 0] = 1.0 - (yy + zz)
        m[0, 1] = xy - wz
        m[0, 2] = xz + wy

        m[1, 0] = xy + wz
        m[1, 1] = 1.0 - (xx + zz)
        m[1, 2] = yz - wx

        m[2, 0] = xz - wy
        m[2, 1] = yz + wx
        m[2, 2] = 1.0 - (xx + yy)

        m[3, 3] = 1.0

        return Matrix(m)

    @staticmethod
    def slerp(start, end, amount):
        if Float.fuzzyCompare(amount, 0.0):
            return start
        elif Float.fuzzyCompare(amount, 1.0):
            return end

        rho = math.acos(start.dot(end))
        return (start * math.sin((1 - amount) * rho) + end * math.sin(amount * rho)) / math.sin(rho)

    @staticmethod
    def rotationTo(v1, v2):
        """Returns a quaternion representing the rotation from vector 1 to vector 2.

        :param v1: :type{Vector} The vector to rotate from.
        :param v2: :type{Vector} The vector to rotate to.
        """

        d = v1.dot(v2)

        if d >= 1.0:
            return Quaternion() # Vectors are equal, no rotation needed.

        if Float.fuzzyCompare(d, -1.0, 1e-6):
            axis = Vector.Unit_X.cross(v1)

            if Float.fuzzyCompare(axis.length(), 0.0):
                axis = Vector.Unit_Y.cross(v1)

            axis = axis.normalized()
            q = Quaternion()
            q.setByAngleAxis(math.pi, axis)
        else:
            s = math.sqrt((1.0 + d) * 2.0)
            invs = 1.0 / s

            c = v1.cross(v2)

            q = Quaternion(
                c.x * invs,
                c.y * invs,
                c.z * invs,
                s * 0.5
            )
            q.normalize()

        return q

    @staticmethod
    def fromMatrix(matrix: Matrix) -> "Quaternion":
        q = Quaternion()
        q.setByMatrix(matrix)
        return q

    @staticmethod
    def fromAngleAxis(angle: float, axis: Vector) -> "Quaternion":
        q = Quaternion()
        q.setByAngleAxis(angle, axis)
        return q

    def __repr__(self):
        return "Quaternion(x={0}, y={1}, z={2}, w={3})".format(self.x, self.y, self.z, self.w)

    def __str__(self):
        return "Q<{0},{1},{2},w={3}>".format(self.x, self.y, self.z, self.w)
