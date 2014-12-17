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

    def test_Create(self):
        box = AxisAlignedBox()

        self.assertEqual(Vector(0.0, 0.0, 0.0), box.minimum)
        self.assertEqual(Vector(0.0, 0.0, 0.0), box.maximum)

        box = AxisAlignedBox(minimum = Vector(), maximum = Vector(10.0, 10.0, 10.0))

        self.assertEqual(Vector(0.0, 0.0, 0.0), box.minimum)
        self.assertEqual(Vector(10.0, 10.0, 10.0), box.maximum)

        box = AxisAlignedBox(10.0, 10.0, 10.0)

        self.assertEqual(Vector(-5.0, -5.0, -5.0), box.minimum)
        self.assertEqual(Vector(5.0, 5.0, 5.0), box.maximum)

        self.assertEqual(-5.0, box.left)
        self.assertEqual(-5.0, box.bottom)
        self.assertEqual(-5.0, box.back)

        self.assertEqual(5.0, box.right)
        self.assertEqual(5.0, box.top)
        self.assertEqual(5.0, box.front)

    def test_Set(self):
        box = AxisAlignedBox()

        box.setLeft(-5.0)
        self.assertEqual(-5.0, box.left)
        self.assertEqual(0.0, box.right)

        box.setBottom(-5.0)
        self.assertEqual(-5.0, box.bottom)
        self.assertEqual(0.0, box.top)

        box.setBack(-5.0)
        self.assertEqual(-5.0, box.back)
        self.assertEqual(0.0, box.front)

        box.setRight(5.0)
        self.assertEqual(-5.0, box.left)
        self.assertEqual(5.0, box.right)

        box.setTop(5.0)
        self.assertEqual(-5.0, box.bottom)
        self.assertEqual(5.0, box.top)

        box.setFront(5.0)
        self.assertEqual(-5.0, box.back)
        self.assertEqual(5.0, box.front)

        box.setRight(-10.0)
        self.assertEqual(-10.0, box.left)
        self.assertEqual(-5.0, box.right)

        box.setTop(-10.0)
        self.assertEqual(-10.0, box.bottom)
        self.assertEqual(-5.0, box.top)

        box.setFront(-10.0)
        self.assertEqual(-10.0, box.back)
        self.assertEqual(-5.0, box.front)

    def test_Intersect(self):
        box = AxisAlignedBox(10.0, 10.0, 10.0)

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

if __name__ == "__main__":
    unittest.main()
