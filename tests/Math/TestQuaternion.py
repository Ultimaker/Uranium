import unittest
import numpy
import math

from UM.Math.Quaternion import Quaternion
from UM.Math.Vector import Vector
from UM.Math.Float import Float
from UM.Math.Matrix import Matrix

class TestQuaternion(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_Create(self):
        q = Quaternion()

        self.assertEqual(q.x, 0.0)
        self.assertEqual(q.y, 0.0)
        self.assertEqual(q.z, 0.0)
        self.assertEqual(q.w, 1.0)

    def test_SetByAxis(self):
        q = Quaternion()

        q.setByAngleAxis(math.pi / 2, Vector.Unit_Z)

        self.assertEqual(q.x, 0.0)
        self.assertEqual(q.y, 0.0)
        self.assertTrue(Float.fuzzyCompare(q.z, math.sqrt(2.0) / 2.0, 1e-6))
        self.assertTrue(Float.fuzzyCompare(q.w, math.sqrt(2.0) / 2.0, 1e-6))

    def test_SetByMatrix(self):
        pass

    def test_Multiply(self):
        q1 = Quaternion()
        q1.setByAngleAxis(math.pi / 2, Vector.Unit_Z)

        q2 = Quaternion()
        q2.setByAngleAxis(math.pi / 2, Vector.Unit_Z)

        q3 = q1 * q2

        q4 = Quaternion()
        q4.setByAngleAxis(math.pi, Vector.Unit_Z)
        self.assertEqual(q3, q4)

    def test_Invert(self):
        q1 = Quaternion()
        q1.setByAngleAxis(math.pi, Vector.Unit_Z)

        q1.invert()

        q2 = Quaternion()
        q2.setByAngleAxis(math.pi, -Vector.Unit_Z)

        self.assertEqual(q1, q2)

    def test_RotateVector(self):
        q1 = Quaternion()
        q1.setByAngleAxis(math.pi / 2, Vector.Unit_Z)

        v = Vector(0, 1, 0)
        v = q1.rotate(v)

        self.assertTrue(Float.fuzzyCompare(v.x, -1.0, 1e-6))
        self.assertTrue(Float.fuzzyCompare(v.y, 0.0, 1e-6))
        self.assertTrue(Float.fuzzyCompare(v.z, 0.0, 1e-6))

    def test_toMatrix(self):
        q1 = Quaternion()
        q1.setByAngleAxis(math.pi / 2, Vector.Unit_Z)

        m1 = q1.toMatrix()

        m2 = Matrix()
        m2.setByRotationAxis(math.pi / 2, Vector.Unit_Z)

        self.assertTrue(Float.fuzzyCompare(m1.at(0, 0), m2.at(0, 0), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(0, 1), m2.at(0, 1), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(0, 2), m2.at(0, 2), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(0, 3), m2.at(0, 3), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(1, 0), m2.at(1, 0), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(1, 1), m2.at(1, 1), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(1, 2), m2.at(1, 2), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(1, 3), m2.at(1, 3), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(2, 0), m2.at(2, 0), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(2, 1), m2.at(2, 1), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(2, 2), m2.at(2, 2), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(2, 3), m2.at(2, 3), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(3, 0), m2.at(3, 0), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(3, 1), m2.at(3, 1), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(3, 2), m2.at(3, 2), 1e-6))
        self.assertTrue(Float.fuzzyCompare(m1.at(3, 3), m2.at(3, 3), 1e-6))

if __name__ == "__main__":
    unittest.main()
