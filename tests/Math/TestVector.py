# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import unittest
import numpy
import pytest

from UM.Math.Vector import Vector

class TestVector(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self._vector = Vector(1,0,0)
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_getData(self):
        numpy.testing.assert_array_almost_equal(self._vector.getData(), numpy.array([1,0,0]))

    def test_angleBetweenVectors(self):
        second_vector = Vector(1,0,0)
        third_vector = Vector(0,1,0)
        fourth_vector = Vector(0,0,1)
        # Check if angle with itself is 0
        self.assertEqual(self._vector.angleToVector(second_vector), 0)
        # Check if angle between the two vectors that are rotated in equal angle but different direction are the same
        self.assertEqual(self._vector.angleToVector(third_vector), self._vector.angleToVector(fourth_vector))

    def test_normalize(self):
        vector = Vector(10, 10, 10)
        assert vector.normalized().length() == pytest.approx(1)

    def test_setValues(self):
        x = 10
        y = 10
        z = 10 
        temp_vector = Vector(x,y,z)
        numpy.testing.assert_array_almost_equal(temp_vector.getData(), numpy.array([x,y,z]))

        temp_vector2 = temp_vector.set(1, 2, 3)
        numpy.testing.assert_array_almost_equal(temp_vector2.getData(), numpy.array([1, 2, 3]))

    def test_negPos(self):
        v = Vector(0, 1, 0)

        self.assertEqual(Vector(0, -1, 0), -v)
        self.assertEqual(Vector(0, 1, 0), v) # - should have no side effects

    def test_compare(self):
        short_vector = Vector(0, 1, 0)
        long_vector = Vector(200, 300, 500)

        assert short_vector < long_vector
        assert long_vector > short_vector
        assert not long_vector == None

    def test_add(self):
        vector = Vector(0, 1, 0)
        vector2 = Vector(1, 0, 1)
        assert vector + vector2 == Vector(1, 1, 1)
        assert vector + vector2.getData() == Vector(1, 1, 1)
        vector += vector2
        assert vector == Vector(1, 1, 1)

    def test_subtract(self):
        vector = Vector(2, 2, 2)
        vector2 = Vector(1, 1, 1)
        assert vector - vector2 == Vector(1, 1, 1)
        assert vector - vector2.getData() == Vector(1, 1, 1)
        assert vector2 - vector == Vector(-1, -1, -1)
        assert vector2 - vector.getData() == Vector(-1, -1, -1)
        vector -= vector2
        assert vector == Vector(1, 1, 1)

    def test_multiply(self):
        vector = Vector(2, 2, 2)
        vector2 = Vector(2, 2, 2)
        assert vector * vector2 == Vector(4, 4, 4)
        assert vector * 2 == Vector(4, 4, 4)
        assert vector.scale(vector2) == Vector(4, 4, 4)
        vector *= vector2
        assert vector == Vector(4, 4, 4)

if __name__ == "__main__":
    unittest.main()
