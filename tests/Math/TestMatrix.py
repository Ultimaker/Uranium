# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import unittest
import numpy
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector

class TestMatrix(unittest.TestCase):
    def setUp(self):
        self._matrix = Matrix()
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_setByQuaternion(self):
        pass
    
    def test_multiply(self):
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

    def test_setByScaleFactor(self):
        self._matrix.setByScaleFactor(0.5)
        numpy.testing.assert_array_almost_equal(self._matrix.getData(), numpy.array([[0.5,0,0,0],[0,0.5,0,0],[0,0,0.5,0],[0,0,0,1]]))

    def test_setByRotation(self):
        pass

    def test_setByTranslation(self):
        self._matrix.setByTranslation(Vector(0,1,0))
        numpy.testing.assert_array_almost_equal(self._matrix.getData(), numpy.array([[1,0,0,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]]))

    def test_setToIdentity(self):
        pass

    def test_getData(self):
        pass

    def test_transposed(self):
        temp_matrix = Matrix()  
        temp_matrix.setByTranslation(Vector(10,10,10))
        temp_matrix = temp_matrix.getTransposed()
        numpy.testing.assert_array_almost_equal(temp_matrix.getData(), numpy.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[10,10,10,1]]))

    def test_dot(self):
        pass

if __name__ == "__main__":
    unittest.main()
