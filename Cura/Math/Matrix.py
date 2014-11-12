import numpy

# Heavily based (in most cases a straight copy with some refactoring) on the excellent 'library' Transformations.py created by Christoph Gohlke.
# This class is a 4x4 homogenous matrix wrapper arround numpy. 

class Matrix(object):
    def __init__(self):
        self._data = self.setToIdentity()
    
    def at(x,y): #TODO add out of index checking
        return self._data[x,y]
    
    def dot(self, matrix):
        self._data = numpy.dot(self._data,matrix.getData())
        
    #Get raw data
    def getData(self):
        return self._data
    
    #Create a 4x4 identity matrix
    def setToIdentity(self):
        self._data = numpy.identity(4)
    
    #Set the matrix by translation vector
    def setByTranslation(self,direction):
        M = numpy.identity(4)
        M[:3, 3] = direction.getData()[:3]
        self._data = M
    
    #Set the matrix based on rotation axis
    def setByRotationAxis(self, angle, direction, point = None):
        sina = math.sin(angle)
        cosa = math.cos(angle)
        direction_data = direction.getData()
        # rotation matrix around unit vector
        R = numpy.diag([cosa, cosa, cosa])
        R += numpy.outer(direction_data, direction_data) * (1.0 - cosa)
        direction *= sina
        R += numpy.array([[ 0.0,         -direction_data[2],  direction_data[1]],
                        [ direction_data[2], 0.0,          -direction_data[0]],
                        [-direction_data[1], direction_data[0],  0.0]])
        M = numpy.identity(4)
        M[:3, :3] = R
        if point is not None:
            # rotation not around origin
            point = numpy.array(point[:3], dtype=numpy.float64, copy=False)
            M[:3, 3] = point - numpy.dot(R, point)
        self._data = M
    
    #Set the matrix by scale by factor wrt origin & direction
    def setByScaleFactor(self, factor, origin=None, direction=None):
        if direction is None:
            # uniform scaling
            M = numpy.diag([factor, factor, factor, 1.0])
            if origin is not None:
                M[:3, 3] = origin[:3]
                M[:3, 3] *= 1.0 - factor
        else:
            # nonuniform scaling
            direction_data = direction.getData()
            factor = 1.0 - factor
            M = numpy.identity(4)
            M[:3, :3] -= factor * numpy.outer(direction_data, direction_data)
            if origin is not None:
                M[:3, 3] = (factor * numpy.dot(origin[:3], direction_data)) * direction_data
        self._data = M
    
    # Set the matrix by proving a quaternion.
    def setByQuaternion(self, quaternion):
        q = numpy.array(quaternion.getData(), dtype=numpy.float64, copy=True)
        n = numpy.dot(q, q)
        if n < _EPS:
            return numpy.identity(4)
        q *= math.sqrt(2.0 / n)
        q = numpy.outer(q, q)
        self._data =  numpy.array([
            [1.0-q[2, 2]-q[3, 3],     q[1, 2]-q[3, 0],     q[1, 3]+q[2, 0], 0.0],
            [    q[1, 2]+q[3, 0], 1.0-q[1, 1]-q[3, 3],     q[2, 3]-q[1, 0], 0.0],
            [    q[1, 3]-q[2, 0],     q[2, 3]+q[1, 0], 1.0-q[1, 1]-q[2, 2], 0.0],
            [                0.0,                 0.0,                 0.0, 1.0]])