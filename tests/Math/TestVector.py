# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import unittest
import numpy

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
        pass

    def test_angleBetweenVectors(self):
        second_vector = Vector(1,0,0)
        third_vector = Vector(0,1,0)
        fourth_vector = Vector(0,0,1)
        # Check if angle with itself is 0
        self.assertEqual(self._vector.angleToVector(second_vector),0)
        # Check if angle between the two vectors that are rotated in equal angle but different direction are the same
        self.assertEqual(self._vector.angleToVector(third_vector),self._vector.angleToVector(fourth_vector))

    def test_normalize(self):
        pass

    def test_setValues(self):
        x = 10
        y = 10
        z = 10 
        temp_vector = Vector(x,y,z)
        numpy.testing.assert_array_almost_equal(temp_vector.getData(), numpy.array([x,y,z]))

    def test_negPos(self):
        v = Vector(0, 1, 0)

        self.assertEqual(Vector(0, -1, 0), -v)
        self.assertEqual(Vector(0, 1, 0), v) # - should have no side effects

if __name__ == "__main__":
    unittest.main()
