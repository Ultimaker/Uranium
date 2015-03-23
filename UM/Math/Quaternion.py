import numpy
import numpy.linalg
import math
import copy

from UM.Math.Vector import Vector
from UM.Math.Float import Float
from UM.Math.Matrix import Matrix

##  Unit Quaternion class based on numpy arrays.
#
#   This class represents a Unit quaternion that can be used for rotations.
#
#   \note The operations that modify this quaternion will ensure the length
#         of the quaternion remains 1. This is done to make this class simpler
#         to use.
#
class Quaternion(object):
    EPS = numpy.finfo(float).eps * 4.0

    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        # Components are stored as XYZW
        self._data = numpy.array([x, y, z, w], dtype=numpy.float32)

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

    ##  Set quaternion by providing rotation about an axis.
    #
    #   \param angle \type{float} Angle in radians
    #   \param axis \type{Vector} Axis of rotation
    def setByAngleAxis(self, angle, axis):
        a = axis.getNormalized().getData()
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

    def getInverse(self):
        result = copy(self)
        result.invert()
        return result

    def invert(self):
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

    def length(self):
        return numpy.linalg.norm(self._data)

    def normalize(self):
        self._data /= numpy.linalg.norm(self._data)

    ## Set quaternion by providing a homogenous (4x4) rotation matrix.
    # \param matrix 4x4 Matrix object
    # \param is_precise
    def setByMatrix(self, matrix, is_precise = False):
        M = numpy.array(matrix.getData(), dtype=numpy.float32, copy=False)[:4, :4]
        if is_precise:
            q = numpy.empty((4, ))
            t = numpy.trace(M)
            if t > M[3, 3]:
                q[0] = t
                q[3] = M[1, 0] - M[0, 1]
                q[2] = M[0, 2] - M[2, 0]
                q[1] = M[2, 1] - M[1, 2]
            else:
                i, j, k = 1, 2, 3
                if M[1, 1] > M[0, 0]:
                    i, j, k = 2, 3, 1
                if M[2, 2] > M[i, i]:
                    i, j, k = 3, 1, 2
                t = M[i, i] - (M[j, j] + M[k, k]) + M[3, 3]
                q[i] = t
                q[j] = M[i, j] + M[j, i]
                q[k] = M[k, i] + M[i, k]
                q[3] = M[k, j] - M[j, k]
            q *= 0.5 / math.sqrt(t * M[3, 3])
        else:
            m00 = M[0, 0]
            m01 = M[0, 1]
            m02 = M[0, 2]
            m10 = M[1, 0]
            m11 = M[1, 1]
            m12 = M[1, 2]
            m20 = M[2, 0]
            m21 = M[2, 1]
            m22 = M[2, 2]
            # symmetric matrix K
            K = numpy.array([[m00-m11-m22, 0.0,         0.0,         0.0],
                            [m01+m10,     m11-m00-m22, 0.0,         0.0],
                            [m02+m20,     m12+m21,     m22-m00-m11, 0.0],
                            [m21-m12,     m02-m20,     m10-m01,     m00+m11+m22]], dtype=numpy.float32)
            K /= 3.0
            # quaternion is eigenvector of K that corresponds to largest eigenvalue
            w, V = numpy.linalg.eigh(K)
            q = V[[3, 0, 1, 2], numpy.argmax(w)]
        if q[0] < 0.0:
            numpy.negative(q, q)
        self._data = q

    def toMatrix(self):
        m = numpy.zeros((4, 4), dtype=numpy.float32)

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

        m[0,0] = 1.0 - (yy + zz)
        m[0,1] = xy - wz
        m[0,2] = xz + wy

        m[1,0] = xy + wz
        m[1,1] = 1.0 - (xx + zz)
        m[1,2] = yz - wx

        m[2,0] = xz - wy
        m[2,1] = yz + wx
        m[2,2] = 1.0 - (xx + yy)

        m[3,3] = 1.0

        return Matrix(m)

    @staticmethod
    def slerp(start, end, amount):
        if Float.fuzzyCompare(amount, 0.0):
            return start
        elif Float.fuzzyCompare(amount, 1.0):
            return end

        rho = math.acos(start.dot(end))
        return (start * math.sin((1 - amount) * rho) + end * math.sin(amount * rho)) / math.sin(rho)

    def __repr__(self):
        return "Quaternion(x={0}, y={1}, z={2}, w={3})".format(self.x, self.y, self.z, self.w)
