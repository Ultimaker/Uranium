import numpy
import math
class Vector(object):
    def __init__(self,x = 0 ,y = 0,z = 0):
        self._data = numpy.array([x, y, z],dtype=numpy.float32)
    
    def setData(self, x = 0,y = 0,z = 0):
        self._data = numpy.array([x,y,z],dtype=numpy.float32)
        
    def getData(self):
        return self._data

    ## Return the x component of this vector
    @property
    def x(self):
        return self._data[0]

    ##  Set the x component of this vector
    #   \param value The value for the x component
    def setX(self, value):
        self._data[0] = value

    ## Return the y component of this vector
    @property
    def y(self):
        return self._data[1]

    ##  Set the y component of this vector
    #   \param value The value for the y component
    def setY(self, value):
        self._data[1] = value

    ## Return the z component of this vector
    @property
    def z(self):
        return self._data[2]

    ##  Set the z component of this vector
    #   \param value The value for the z component
    def setZ(self, value):
        self._data[2] = value
    
    ## Get the angle from this vector to another
    def angleToVector(self, vector,):
        v0 = numpy.array(self._data, dtype=numpy.float32, copy=False)
        v1 = numpy.array(vector.getData(), dtype = numpy.float32, copy=False)
        dot = numpy.sum(v0 * v1)
        dot /= self._normalizeVector(v0) * self._normalizeVector(v1)
        return numpy.arccos(numpy.fabs(dot))
    
    
    def normalize(self, data):
        self._data = self._normalizeVector(self._data)
    
    ## Return length, i.e. Euclidean norm, of ndarray along axis.
    def _normalizeVector(self, data):
        data = numpy.array(data, dtype=numpy.float32, copy=True)
        if data.ndim == 1:
            return math.sqrt(numpy.dot(data, data))
        data *= data
        out = numpy.atleast_1d(numpy.sum(data))
        numpy.sqrt(out, out)
        return out

        
        
