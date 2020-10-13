# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import unittest
import numpy
import pytest

from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
import copy

class TestMatrix(unittest.TestCase):
    def setUp(self):
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

    def test_multiplyCopy(self):
        temp_matrix = Matrix()
        temp_matrix.setByTranslation(Vector(10, 10, 10))
        temp_matrix2 = Matrix()
        temp_matrix2.setByScaleFactor(0.5)
        result = temp_matrix.multiply(temp_matrix2, copy=True)
        assert temp_matrix != result 
        numpy.testing.assert_array_almost_equal(result.getData(), numpy.array([[0.5, 0, 0, 10], [0, 0.5, 0, 10], [0, 0, 0.5, 10], [0, 0, 0, 1]]))

    def test_preMultiply(self):
        temp_matrix = Matrix()
        temp_matrix.setByTranslation(Vector(10,10,10))
        temp_matrix2 = Matrix()
        temp_matrix2.setByScaleFactor(0.5)
        temp_matrix.preMultiply(temp_matrix2)
        numpy.testing.assert_array_almost_equal(temp_matrix.getData(), numpy.array([[0.5,0,0,5],[0,0.5,0,5],[0,0,0.5,5],[0,0,0,1]]))

    def test_preMultiplyCopy(self):
        temp_matrix = Matrix()
        temp_matrix.setByTranslation(Vector(10,10,10))
        temp_matrix2 = Matrix()
        temp_matrix2.setByScaleFactor(0.5)
        result = temp_matrix.preMultiply(temp_matrix2, copy = True)
        assert result != temp_matrix
        numpy.testing.assert_array_almost_equal(result.getData(), numpy.array([[0.5,0,0,5],[0,0.5,0,5],[0,0,0.5,5],[0,0,0,1]]))

    def test_setByScaleFactor(self):
        matrix = Matrix()
        matrix.setByScaleFactor(0.5)
        numpy.testing.assert_array_almost_equal(matrix.getData(), numpy.array([[0.5,0,0,0],[0,0.5,0,0],[0,0,0.5,0],[0,0,0,1]]))

        assert matrix.getScale() == Vector(0.5, 0.5, 0.5)

    def test_scaleByFactor(self):
        matrix = Matrix()
        matrix.scaleByFactor(2)
        assert matrix.getScale() == Vector(2, 2, 2)

    def test_setByRotation(self):
        pass

    def test_setByTranslation(self):
        matrix = Matrix()
        matrix.setByTranslation(Vector(0,1,0))
        numpy.testing.assert_array_almost_equal(matrix.getData(), numpy.array([[1,0,0,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]]))

    def test_deepcopy(self):
        matrix = Matrix()

        # Set some data
        matrix.setRow(1, [1, 2, 3])
        matrix.setColumn(2, [3, 4, 5])

        copied_matrix = copy.deepcopy(matrix)
        assert copied_matrix == matrix

    def test_compare(self):
        matrix = Matrix()
        matrix2 = Matrix()

        assert matrix == matrix
        assert not matrix == "zomg"

        matrix._data = None
        matrix2._data = None
        assert matrix == matrix2

    def test_translate(self):
        matrix = Matrix()
        matrix.translate(Vector(1, 1, 1))
        assert matrix.getTranslation() == Vector(1, 1, 1)
        matrix.translate(Vector(2, 3, 4))
        assert matrix.getTranslation() == Vector(3, 4, 5)

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

    def test_invalidAt(self):
        matrix = Matrix()
        with pytest.raises(IndexError):
            matrix.at(12, 13)

    def test_invalidSetRow(self):
        matrix = Matrix()
        with pytest.raises(IndexError):
            matrix.setRow(12, [1., 2., 3.])
            matrix.setRow(-1, [2., 3., 4.])

    def test_invalidSetColumn(self):
        matrix = Matrix()
        with pytest.raises(IndexError):
            matrix.setColumn(12, [1., 2., 3.])
            matrix.setColumn(-1, [2., 3., 4.])