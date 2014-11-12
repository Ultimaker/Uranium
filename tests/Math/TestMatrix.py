import unittest
import numpy
from Cura.Math.Matrix import Matrix
from Cura.Math.Vector import Vector

class TestMatrix(unittest.TestCase):
    def setUp(self):
        self._matrix = Matrix()
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_SetByQuaternion(self):
        pass
    
    def test_Multiply(self):
        temp_matrix = Matrix()
        temp_matrix.setByTranslation(Vector(10,10,10))
        temp_matrix2 = Matrix()
        temp_matrix2.setByScaleFactor(0.5)
        temp_matrix.multiply(temp_matrix2)
        numpy.testing.assert_array_almost_equal(temp_matrix.getData(), numpy.array([[0.5,0,0,10],[0,0.5,0,10],[0,0,0.5,10],[0,0,0,1]]))
    
    def test_preMultiply(self):
        temp_matrix = Matrix()
        temp_matrix.setByTranslation(Vector(10,10,10))
        temp_matrix2 = Matrix()
        temp_matrix2.setByScaleFactor(0.5)
        temp_matrix.preMultiply(temp_matrix2)
        numpy.testing.assert_array_almost_equal(temp_matrix.getData(), numpy.array([[0.5,0,0,5],[0,0.5,0,5],[0,0,0.5,5],[0,0,0,1]]))

    def test_SetByScaleFactor(self):
        self._matrix.setByScaleFactor(0.5)
        numpy.testing.assert_array_almost_equal(self._matrix.getData(), numpy.array([[0.5,0,0,0],[0,0.5,0,0],[0,0,0.5,0],[0,0,0,1]]))

    def test_SetByRotation(self):
        pass

    def test_SetByTranslation(self):
        self._matrix.setByTranslation(Vector(0,1,0))
        numpy.testing.assert_array_almost_equal(self._matrix.getData(), numpy.array([[1,0,0,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]]))

    def test_SetToIdentity(self):
        pass

    def test_GetData(self):
        pass

    def test_Dot(self):
        pass

if __name__ == "__main__":
    unittest.main()
