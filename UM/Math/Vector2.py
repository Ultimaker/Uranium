# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import numpy
import numpy.linalg


##  Simple 2D-vector class based on numpy arrays.
#
#   This class represents a 2-dimensional vector.
class Vector2(object):
    Unit_X = None   # type: Vector2
    Unit_Y = None   # type: Vector2

    ##  Creates a new 2D vector.
    #
    #   Usage:
    #    - Vector2(x,y):          Creates a vector [x,y].
    #    - Vector2(data = [x,y]): Creates a vector [x,y].
    #    - Vector2():             Creates a vector [0,0].
    #
    #   \param data The numpy array of data to fill the vector with.
    def __init__(self, *args, **kwargs):
        if len(args) == 2: #X and Y specified.
            self._data = numpy.array([args[0], args[1]], dtype=numpy.float32)
        elif "data" in kwargs: #Data parameter specified.
            self._data = kwargs["data"].copy()
        else: #Nothing specified. Fill in 0.
            self._data = numpy.zeros(2, dtype=numpy.float32)

    ##  Computes the generalised cross product of this vector with another.
    #
    #   \param other The vector to compute the cross product with.
    #   \return The generalised cross product.
    def cross(self, other):
        return self._data[0] * other._data[1] - self._data[1] * other._data[0]

    ##  Computes the dot product of this vector and another.
    #
    #   \param other The vector to compute the dot product with.
    #   \return The dot product of the two vectors.
    def dot(self, other):
        return numpy.dot(self._data, other._data)

    ##  Gets the numpy array with the data.
    #
    #   \return A numpy array with the data of this vector.
    def getData(self):
        return self._data

    ##  Gets the Euclidean length of this vector.
    #
    #   \return The length of this vector.
    def length(self):
        return numpy.linalg.norm(self._data)

    ##  Gets a vector that is perpendicular to this vector.
    #
    #   There are exactly two vectors perpendicular. This method gets the
    #   perpendicular vector that is left of this vector.
    #
    #   \return A perpendicular vector.
    def perpendicular(self):
        return Vector2(-self._data[1], self._data[0])

    ##  Changes the x-component of this vector.
    #
    #   \param x The new x-component of the vector.
    def setX(self, x):
        self._data[0] = x

    ##  Changes the y-component of this vector.
    #
    #   \param y The new y-component of the vector.
    def setY(self, y):
        self._data[1] = y

    ##  Gets the x-component of the vector.
    #
    #   \return The x-component of the vector.
    @property
    def x(self):
        return self._data[0]

    ##  Gets the y-component of the vector.
    #
    #   \return The y-component of the vector.
    @property
    def y(self):
        return self._data[1]

    ##  Adds the specified vector to this vector element-wise.
    #
    #   \param other The vector that must be added to this vector.
    #   \return The result of the adding.
    def __add__(self, other):
        result = Vector2(data = self._data)
        result += other
        return result

    ##  Adds the specified vector in-place to this vector element-wise.
    #
    #   \param other The vector that must be added to this vector.
    def __iadd__(self, other):
        if type(other) is float:
            self._data[0] += other
            self._data[1] += other
        elif type(other) is Vector2:
            self._data[0] += other._data[0]
            self._data[1] += other._data[1]
        else:
            raise NotImplementedError()

        return self

    ##  Divides this vector by the specified vector element-wise.
    #
    #   \param other The vector by which this vector must be divided.
    #   \return The result of the division.
    def __truediv__(self, other):
        result = Vector2(data = self._data)
        result /= other
        return result

    ##  Divides this vector in-place by the specified vector element-wise.
    #
    #   \param other The vector by which this vector must be divided.
    def __itruediv__(self, other):
        if type(other) is float or type(other) is int:
            self._data /= other
            return self
        else:
            raise NotImplementedError()

    ##  Divides this vector by the specified vector element-wise.
    #
    #   \param other The vector by which this vector must be divided.
    #   \return The result of the division.
    def __rtruediv__(self, other):
        if type(other) is float:
            result = numpy.float32(other) / self._data
            return Vector2(result[0], result[1])
        else:
            raise NotImplementedError()

    ##  Multiplies the specified vector with this vector element-wise.
    #
    #   \param other The vector that must be multiplied with this vector.
    #   \return The result of the multiplication.
    def __mul__(self, other):
        result = Vector2(data = self._data)
        result *= other
        return result

    ##  Multiplies the specified vector in-place with this vector element-wise.
    #
    #   \param other The vector that must be multiplied with this vector.
    def __imul__(self, other):
        if type(other) is float:
            self._data[0] *= other
            self._data[1] *= other
        elif type(other) is Vector2:
            self._data[0] *= other._data[0]
            self._data[1] *= other._data[1]
        else:
            raise NotImplementedError()

        return self
    
    ##  Multiplies the specified vector with this vector element-wise.
    #
    #   \param other The vector that must be multiplied with this vector.
    def __rmul__(self, other):
        result = Vector2(data = self._data)
        result *= other
        return result

    ##  Negates the vector, resulting in a vector with the opposite direction.
    #
    #   \return The negated vector.
    def __neg__(self):
        return Vector2(data = -self._data)

    ##  Subtracts the specified vector from this vector element-wise.
    #
    #   \param other The vector that must be subtracted from this vector.
    #   \return The result of the subtraction.
    def __sub__(self, other):
        result = Vector2(data = self._data)
        result -= other
        return result
    
    ##  Subtracts the specified vector in-place from this vector element-wise.
    #
    #   \param other The vector that must be subtracted from this vector.
    def __isub__(self, other):
        if type(other) is float:
            self._data[0] -= other
            self._data[1] -= other
        elif type(other) is Vector2:
            self._data[0] -= other._data[0]
            self._data[1] -= other._data[1]
        else:
            raise NotImplementedError()
        return self

    ##  Gives a programmer-readable string representation of this vector.
    #
    #   The format is: [x,y]
    #
    #   \return A string representation of this vector.
    def __str__(self):
        return "[" + str(self._data[0]) + "," + str(self._data[1]) + "]"