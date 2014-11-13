import numpy
import math
class Vector(object):
    def __init__(self,x = 0 ,y = 0,z = 0):
        self._data = numpy.array([x, y, z])
    
    def setData(self, x = 0,y = 0,z = 0):
        self._data = numpy.array([x,y,z])
        
    def getData(self):
        return self._data
    
    ## Get the angle from this vector to another
    def angleToVector(self, vector,):
        v0 = numpy.array(self._data, dtype=numpy.float64, copy=False)
        v1 = numpy.array(vector.getData(), dtype = numpy.float64, copy=False)
        dot = numpy.sum(v0 * v1)
        dot /= self._normalizeVector(v0) * self._normalizeVector(v1)
        return numpy.arccos(numpy.fabs(dot))
    
    
    def normalize(data):
        self._data = self._normalizeVector(self._data)
    
    ## Return length, i.e. Euclidean norm, of ndarray along axis.
    def _normalizeVector(self,data):
        data = numpy.array(data, dtype=numpy.float64, copy=True)
        if data.ndim == 1:
            return math.sqrt(numpy.dot(data, data))
        data *= data
        out = numpy.atleast_1d(numpy.sum(data))
        numpy.sqrt(out, out)
        return out

        
        