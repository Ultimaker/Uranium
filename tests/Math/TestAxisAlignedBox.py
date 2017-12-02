# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Vector import Vector
from UM.Math.Ray import Ray

import unittest

class TestAxisAlignedBox(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass

    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_create(self):
        box = AxisAlignedBox()

        self.assertEqual(Vector(0.0, 0.0, 0.0), box.minimum)
        self.assertEqual(Vector(0.0, 0.0, 0.0), box.maximum)
        self.assertFalse(box.isValid())

        box = AxisAlignedBox(minimum = Vector(), maximum = Vector(10.0, 10.0, 10.0))

        self.assertEqual(Vector(0.0, 0.0, 0.0), box.minimum)
        self.assertEqual(Vector(10.0, 10.0, 10.0), box.maximum)
        self.assertTrue(box.isValid())

    def test_set(self):
        box = AxisAlignedBox()

        box = box.set(left=-5.0)
        self.assertEqual(-5.0, box.left)
        self.assertEqual(0.0, box.right)
        self.assertFalse(box.isValid())

        box = box.set(bottom=-5.0)
        self.assertEqual(-5.0, box.bottom)
        self.assertEqual(0.0, box.top)
        self.assertFalse(box.isValid())

        box = box.set(back=-5.0)
        self.assertEqual(-5.0, box.back)
        self.assertEqual(0.0, box.front)
        self.assertTrue(box.isValid())

        box = box.set(right=5.0)
        self.assertEqual(-5.0, box.left)
        self.assertEqual(5.0, box.right)
        self.assertTrue(box.isValid())

        box = box.set(top=5.0)
        self.assertEqual(-5.0, box.bottom)
        self.assertEqual(5.0, box.top)
        self.assertTrue(box.isValid())

        box = box.set(front=5.0)
        self.assertEqual(-5.0, box.back)
        self.assertEqual(5.0, box.front)
        self.assertTrue(box.isValid())

        box = box.set(right=-10.0)
        self.assertEqual(-10.0, box.left)
        self.assertEqual(-5.0, box.right)
        self.assertTrue(box.isValid())

        box = box.set(top=-10.0)
        self.assertEqual(-10.0, box.bottom)
        self.assertEqual(-5.0, box.top)
        self.assertTrue(box.isValid())

        box = box.set(front=-10.0)
        self.assertEqual(-10.0, box.back)
        self.assertEqual(-5.0, box.front)
        self.assertTrue(box.isValid())

    def test_add(self):
        box1 = AxisAlignedBox(minimum = Vector(-10.0, -10.0, -10.0), maximum = Vector(0.0, 0.0, 0.0))
        box2 = AxisAlignedBox(minimum = Vector(0.0, 0.0, 0.0), maximum = Vector(10.0, 10.0, 10.0))

        joined = box1 + box2

        self.assertEqual(Vector(-10.0, -10.0, -10.0), joined.minimum)
        self.assertEqual(Vector(10.0, 10.0, 10.0), joined.maximum)
        self.assertTrue(joined.isValid())

    def test_intersectsRay(self):
        box = AxisAlignedBox(minimum=Vector(-5,-5,-5), maximum=Vector(5.0, 5.0, 5.0))

        ray = Ray(Vector(-10.0, 0.0, 0.0), Vector(1.0, 0.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(5.0, result[0])
        self.assertEqual(15.0, result[1])

        ray = Ray(Vector(10.0, 0.0, 0.0), Vector(-1.0, 0.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(5.0, result[0])
        self.assertEqual(15.0, result[1])

        ray = Ray(Vector(0.0, -10.0, 0.0), Vector(0.0, 1.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(5.0, result[0])
        self.assertEqual(15.0, result[1])

        ray = Ray(Vector(0.0, 10.0, 0.0), Vector(0.0, -1.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(5.0, result[0])
        self.assertEqual(15.0, result[1])

        ray = Ray(Vector(0.0, 0.0, -10.0), Vector(0.0, 0.0, 1.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(5.0, result[0])
        self.assertEqual(15.0, result[1])

        ray = Ray(Vector(0.0, 0.0, 10.0), Vector(0.0, 0.0, -1.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(5.0, result[0])
        self.assertEqual(15.0, result[1])

        ray = Ray(Vector(15.0, 0.0, 0.0), Vector(0.0, 1.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertEqual(False, result)

        ray = Ray(Vector(15.0, 15.0, 0.0), Vector(-1.0, -1.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(10.0, result[0])
        self.assertEqual(20.0, result[1])

        ray = Ray(Vector(10.0, -15.0, 0.0), Vector(-1.0, 1.0, 0.0))
        result = box.intersectsRay(ray)
        self.assertNotEqual(False, result)
        self.assertEqual(10.0, result[0])
        self.assertEqual(15.0, result[1])

    def test_intersectsBox(self):
        box1 = AxisAlignedBox(minimum = Vector(5.0, 5.0, 5.0), maximum = Vector(10.0, 10.0, 10.0))

        box2 = AxisAlignedBox(minimum = Vector(-10.0, -10.0, -10.0), maximum = Vector(-5.0, -5.0, -5.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.NoIntersection)

        box2 = AxisAlignedBox(minimum = Vector(-10.0, 0.0, -10.0), maximum = Vector(-5.0, 10.0, -5.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.NoIntersection)

        box2 = AxisAlignedBox(minimum = Vector(0.0, -10.0, -10.0), maximum = Vector(10.0, -5.0, -5.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.NoIntersection)

        box2 = AxisAlignedBox(minimum = Vector(-10.0, -10.0, 0.0), maximum = Vector(-5.0, -5.0, 10.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.NoIntersection)

        box2 = AxisAlignedBox(minimum = Vector(0.0, 0.0, 0.0), maximum = Vector(7.5, 7.5, 7.5))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.PartialIntersection)

        box2 = AxisAlignedBox(minimum = Vector(5.0, 0.0, 5.0), maximum = Vector(10.0, 7.5, 10.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.PartialIntersection)

        box2 = AxisAlignedBox(minimum = Vector(6.0, 6.0, 6.0), maximum = Vector(9.0, 9.0, 9.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.FullIntersection)

        box2 = AxisAlignedBox(minimum = Vector(5.0, 5.0, 5.0), maximum = Vector(10.0, 10.0, 10.0))
        self.assertEqual(box1.intersectsBox(box2), AxisAlignedBox.IntersectionResult.FullIntersection)

if __name__ == "__main__":
    unittest.main()
