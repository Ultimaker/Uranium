# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import numpy
import numpy.linalg
import math
from copy import deepcopy
from UM.Math.Float import Float

# Disable divide-by-zero warnings so that 1.0 / (1.0, 0.0, 0.0) returns (1.0, Inf, Inf) without complaining
numpy.seterr(divide="ignore")

##  Simple 3D-vector class based on numpy arrays.
#
#   This class represents a 3-dimensional vector.
class Vector(object):
    Unit_X = None
    Unit_Y = None
    Unit_Z = None

    def __init__(self, *args, **kwargs):
        if len(args) == 3:
            self._data = numpy.array([args[0], args[1], args[2]],dtype=numpy.float32)
        elif "data" in kwargs:
            self._data = kwargs["data"].copy()
        else:
            self._data = numpy.zeros(3, dtype=numpy.float32)
    
    ##  Set the data of the vector
    #   \param x X coordinate of vector.
    #   \param y Y coordinate of vector.
    #   \param z Z coordinate of vector.
    def setData(self, x = 0,y = 0,z = 0):
        self._data = numpy.array([x,y,z],dtype=numpy.float32)
    
    def flip(self):
        self._data[0] = -1 * self._data[0]
        self._data[1] = -1 * self._data[1]
        self._data[2] = -1 * self._data[2]
        return self
    
    ##  Get numpy array with the data
    #   \returns numpy array of length 3 holding xyz data.
    def getData(self):
        return self._data

    ##  Return the x component of this vector
    @property
    def x(self):
        return numpy.float32(self._data[0])

    ##  Set the x component of this vector
    #   \param value The value for the x component
    def setX(self, value):
        self._data[0] = numpy.float32(value)

    ##  Return the y component of this vector
    @property
    def y(self):
        return numpy.float32(self._data[1])

    ##  Set the y component of this vector
    #   \param value The value for the y component
    def setY(self, value):
        self._data[1] = numpy.float32(value)

    ## Return the z component of this vector
    @property
    def z(self):
        return numpy.float32(self._data[2])

    ##  Set the z component of this vector
    #   \param value The value for the z component
    def setZ(self, value):
        self._data[2] = numpy.float32(value)
    
    ##  Get the angle from this vector to another
    def angleToVector(self, vector):
        v0 = numpy.array(self._data, dtype=numpy.float32, copy=False)
        v1 = numpy.array(vector.getData(), dtype = numpy.float32, copy=False)
        dot = numpy.sum(v0 * v1)
        dot /= self._normalizeVector(v0) * self._normalizeVector(v1)
        return numpy.arccos(numpy.fabs(dot))
    
    def normalize(self):
        l = self.length()
        if l != 0:
            self._data /= l
        return self

    def getNormalized(self):
        other = deepcopy(self)
        return other.normalize()
    
    ##  Return length, i.e. Euclidean norm, of ndarray along axis.
    def _normalizeVector(self, data):
        data = numpy.array(data, dtype=numpy.float32, copy=True)
        if data.ndim == 1:
            return math.sqrt(numpy.dot(data, data))
        data *= data
        out = numpy.atleast_1d(numpy.sum(data))
        numpy.sqrt(out, out)
        return out

    def length(self):
        return numpy.linalg.norm(self._data)

    def dot(self, other):
        return numpy.dot(self._data, other._data)

    def cross(self, other):
        result = numpy.cross(self._data, other._data)
        return Vector(result[0], result[1], result[2])

    def multiply(self, matrix):
        d = numpy.empty(4, dtype=numpy.float32)
        d[0] = self._data[0]
        d[1] = self._data[1]
        d[2] = self._data[2]
        d[3] = 1.0

        d = d.dot(matrix.getData())

        return Vector(d[0], d[1], d[2])

    def preMultiply(self, matrix):
        d = numpy.empty(4, dtype=numpy.float32)
        d[0] = self._data[0]
        d[1] = self._data[1]
        d[2] = self._data[2]
        d[3] = 1.0

        d = matrix.getData().dot(d)

        return Vector(d[0], d[1], d[2])

    ##  Scale a vector by another vector.
    #
    #   This will do a component-wise multiply of the two vectors.
    def scale(self, other):
        return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

    def __eq__(self, other):
        return Float.fuzzyCompare(self.x, other.x, 1e-6) and Float.fuzzyCompare(self.y, other.y, 1e-6) and Float.fuzzyCompare(self.z, other.z, 1e-6)

    def __add__(self, other):
        v = Vector(data = self._data)
        v += other
        return v

    def __iadd__(self, other):
        if type(other) is float:
            self._data[0] += other
            self._data[1] += other
            self._data[2] += other
        elif type(other) is Vector:
            self._data[0] += other._data[0]
            self._data[1] += other._data[1]
            self._data[2] += other._data[2]
        else:
            raise NotImplementedError()

        return self

    def __sub__(self, other):
        v = Vector(data = self._data)
        v -= other
        return v

    def __isub__(self, other):
        if type(other) is float:
            self._data[0] -= other
            self._data[1] -= other
            self._data[2] -= other
        elif type(other) is Vector:
            self._data[0] -= other._data[0]
            self._data[1] -= other._data[1]
            self._data[2] -= other._data[2]
        else:
            raise NotImplementedError()

        return self

    def __mul__(self, other):
        v = deepcopy(self)
        v *= other
        return v

    def __imul__(self, other):
        t = type(other)
        if t is float or t is numpy.float32 or t is numpy.float64 or t is int:
            self._data *= other
            return self
        elif t is Vector: #Element-wise multiplication.
            self._data[0] *= other._data[0]
            self._data[1] *= other._data[1]
            self._data[2] *= other._data[2]
            return self
        else:
            raise NotImplementedError()

    def __rmul__(self, other):
        v = deepcopy(self)
        v *= other
        return v

    def __truediv__(self, other):
        v = Vector(data = self._data)
        v /= other
        return v

    def __itruediv__(self, other):
        if type(other) is float or type(other) is int:
            self._data /= other
            return self
        if type(other) is Vector:
            self._data /= other._data
            return self
        else:
            raise NotImplementedError()

    def __rtruediv__(self, other):
        if type(other) is float:
            v = numpy.float32(other) / self._data
            return Vector(v[0], v[1], v[2])
        else:
            raise NotImplementedError()

    def __neg__(self):
        return Vector(data = -self._data)

    def __repr__(self):
        return "Vector({0}, {1}, {2})".format(self._data[0], self._data[1], self._data[2])

    def __lt__(self, other):
        return self._data[0] < other._data[0] and self._data[1] < other._data[1] and self._data[2] < other._data[2]

    def __gt__(self, other):
        return self._data[0] > other._data[0] and self._data[1] > other._data[1] and self._data[2] > other._data[2]

    def __le__(self, other):
        return self._data[0] <= other._data[0] and self._data[1] <= other._data[1] and self._data[2] <= other._data[2]

    def __ge__(self, other):
        return self._data[0] >= other._data[0] and self._data[1] >= other._data[1] and self._data[2] >= other._data[2]

Vector.Unit_X = Vector(1, 0, 0)
Vector.Unit_Y = Vector(0, 1, 0)
Vector.Unit_Z = Vector(0, 0, 1)
