import numpy
import math

# Heavily based (in most cases a straight copy with some refactoring) on the excellent 'library' Transformations.py created by Christoph Gohlke.
# This class is a 4x4 homogenous matrix wrapper arround numpy. 

class Matrix(object):
    def __init__(self, data = numpy.identity(4)):
        self._data = data
    
    def at(x,y): #TODO add out of index checking
        return self._data[x,y]
    
    def multiply(self, matrix):
        self._data = numpy.dot(self._data, matrix.getData())
    
    def preMultiply(self, matrix):
        self._data = numpy.dot(matrix.getData(),self._data)
        
    # Get raw data.
    # \returns 4x4 numpy array
    def getData(self):
        return self._data
    
    # Create a 4x4 identity matrix. This overwrites any existing data.
    def setToIdentity(self):
        self._data = numpy.identity(4)
        
    # Invert the matrix
    def invert(self):
        self._data = numpy.linalg.inv(self._data)
    
    # Return a inverted copy of the matrix.
    # \returns The invertex matrix.
    def getInverse(self):
        return Matrix(numpy.linalg.inv(self._data))
    
    # Translate the matrix based on Vector.
    # \param direction The vector by which the matrix needs to be translated.
    def translate(self, direction):
        translation_matrix = Matrix()
        translation_matrix.setByTranslation(direction)
        self.multiply(translation_matrix)
    
    # Set the matrix by translation vector. This overwrites any existing data.
    # \param direction The vector by which the (unit) matrix needs to be translated.
    def setByTranslation(self, direction):
        M = numpy.identity(4)
        M[:3, 3] = direction.getData()[:3]
        self._data = M
    
    # Rotate the matrix based on rotation axis
    # \param angle The angle by which matrix needs to be rotated.
    # \param direction Axis by which the matrix needs to be rotated about.
    # \param point Point where from where the rotation happens. If None, origin is used.
    def rotateByAxis(self, angle, direction, point = None):
        rotation_matrix = Matrix()
        rotation_matrix.setByRotationAxis(angle, direction, point)
        self.multiply(rotation_matrix)
    
    # Set the matrix based on rotation axis. This overwrites any existing data.
    # \param angle The angle by which matrix needs to be rotated.
    # \param direction Axis by which the matrix needs to be rotated about.
    # \param point Point where from where the rotation happens. If None, origin is used.
    def setByRotationAxis(self, angle, direction, point = None):
        sina = math.sin(angle)
        cosa = math.cos(angle)
        direction_data = direction.getData()
        # rotation matrix around unit vector
        R = numpy.diag([cosa, cosa, cosa])
        R += numpy.outer(direction_data, direction_data) * (1.0 - cosa)
        direction_data *= sina
        R += numpy.array([[ 0.0, -direction_data[2], direction_data[1]],
                        [ direction_data[2], 0.0, -direction_data[0]],
                        [-direction_data[1], direction_data[0], 0.0]])
        M = numpy.identity(4)
        M[:3, :3] = R
        if point is not None:
            # rotation not around origin
            point = numpy.array(point[:3], dtype=numpy.float64, copy=False)
            M[:3, 3] = point - numpy.dot(R, point)
        self._data = M
    
    # Scale the matrix by factor wrt origin & direction.
    # \param factor The factor by which to scale
    # \param origin From where does the scaling need to be done
    # \param direction In what direction is the scaling (if None, it's uniform)
    def scaleByFactor(self, factor, origin = None, direction = None):
        scale_matrix = Matrix()
        scale_matrix.setByScaleFactor(factor, origin, direction)
        self.multiply(scale_matrix)
    
    # Set the matrix by scale by factor wrt origin & direction. This overwrites any existing data
    # \param factor The factor by which to scale
    # \param origin From where does the scaling need to be done
    # \param direction In what direction is the scaling (if None, it's uniform)
    def setByScaleFactor(self, factor, origin = None, direction = None):
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
    
    # Set the matrix by proving a quaternion. This overwrites any existing data
    # \param quaternion The quaternion used to set the matrix data.
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