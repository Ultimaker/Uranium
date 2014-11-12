class Vector(object):
    def __init__(self,x = 0 ,y = 0,z = 0):
        self._data = np.array([x, y, z])
    
    def setData(self, x = 0,y = 0,z = 0):
        self._data = np.array([x,y,z])
        
    def getData(self):
        return self._data
    
    # Get the angle from this vector to another
    def angleToVector(self, vector):
        v0 = numpy.array(self._data, dtype=numpy.float64, copy=False)
        v1 = numpy.array(vector, dtype=numpy.float64, copy=False)
        dot = numpy.sum(v0 * v1, axis=axis)
        dot /= vector_norm(v0, axis=axis) * vector_norm(v1, axis=axis)
        return numpy.arccos(dot if directed else numpy.fabs(dot))
        
        