# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Math.Ray import Ray

import unittest

class TestPlane(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_create(self):
        p = Plane()
        self.assertEqual(Vector(), p.normal)
        self.assertEqual(0.0, p.distance)

        p = Plane(Vector.Unit_Y, 1.0)
        self.assertEqual(Vector.Unit_Y, p.normal)
        self.assertEqual(1.0, p.distance)

    def test_intersects(self):
        p = Plane(Vector.Unit_Y, 0.0)

        r = Ray(Vector(0, 10, 0), -Vector.Unit_Y)
        result = p.intersectsRay(r)
        self.assertNotEqual(False, result)
        self.assertEqual(10.0, result)

        r = Ray(Vector(0, -10, 0), Vector.Unit_Y)
        result = p.intersectsRay(r)
        self.assertNotEqual(False, result)
        self.assertEqual(10.0, result)

        r = Ray(Vector(0, 10, 0), Vector.Unit_Y)
        self.assertEqual(False, p.intersectsRay(r))

        r = Ray(Vector(0, 0, 0), Vector.Unit_X)
        self.assertEqual(False, p.intersectsRay(r))


if __name__ == "__main__":
    unittest.main()
