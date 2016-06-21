# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode

from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion
from UM.Math.Matrix import Matrix
from UM.Math.Float import Float

import unittest
import math

class SceneNodeTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setPosition(self):
        node = SceneNode()

        self.assertEqual(node.getPosition(), Vector(0, 0, 0))

        node.setPosition(Vector(0, 0, 10))

        self.assertEqual(node.getPosition(), Vector(0, 0, 10))

        node.setPosition(Vector(0, 0, 10))

        self.assertEqual(node.getPosition(), Vector(0, 0, 10))

    def test_translate(self):
        node = SceneNode()

        self.assertEqual(node.getPosition(), Vector(0, 0, 0))

        node.translate(Vector(0, 0, 10))

        self.assertEqual(node.getPosition(), Vector(0, 0, 10))

        node.translate(Vector(0, 0, 10))

        self.assertEqual(node.getPosition(), Vector(0, 0, 20))

    def test_setOrientation(self):
        node = SceneNode()

        self.assertEqual(node.getOrientation(), Quaternion())

        node.setOrientation(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        self.assertEqual(node.getOrientation(), Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node.setOrientation(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        self.assertEqual(node.getOrientation(), Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

    def test_rotate(self):
        node = SceneNode()

        self.assertEqual(node.getOrientation(), Quaternion())

        node.rotate(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        self.assertEqual(node.getOrientation(), Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node.rotate(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        self.assertEqual(node.getOrientation(), Quaternion.fromAngleAxis(math.pi / 2, Vector.Unit_Z))

    def test_setScale(self):
        node = SceneNode()

        self.assertEqual(node.getScale(), Vector(1, 1, 1))

        node.setScale(Vector(1.5, 1.5, 1.5))

        self.assertEqual(node.getScale(), Vector(1.5, 1.5, 1.5))

        node.setScale(Vector(1.5, 1.5, 1.5))

        self.assertEqual(node.getScale(), Vector(1.5, 1.5, 1.5))

    def test_scale(self):
        node = SceneNode()

        self.assertEqual(node.getScale(), Vector(1, 1, 1))

        node.scale(Vector(1.5, 1.5, 1.5))

        self.assertEqual(node.getScale(), Vector(1.5, 1.5, 1.5))

        node.scale(Vector(1.5, 1.5, 1.5))

        self.assertEqual(node.getScale(), Vector(2.25, 2.25, 2.25))

    def test_translateWorld(self):
        node1 = SceneNode()

        node2 = SceneNode(node1)

        self.assertEqual(node2.getWorldPosition(), Vector(0, 0, 0))

        node1.translate(Vector(0, 0, 10))

        self.assertEqual(node1.getWorldPosition(), Vector(0, 0, 10))
        self.assertEqual(node2.getWorldPosition(), Vector(0, 0, 10))

        node2.translate(Vector(0, 0, 10))

        self.assertEqual(node1.getWorldPosition(), Vector(0, 0, 10))
        self.assertEqual(node2.getWorldPosition(), Vector(0, 0, 20))

        node1.rotate(Quaternion.fromAngleAxis(math.pi / 2, Vector.Unit_Y))

        self.assertEqual(node1.getWorldPosition(), Vector(0, 0, 10))
        self.assertEqual(node2.getWorldPosition(), Vector(10, 0, 10))

        node2.translate(Vector(0, 0, 10))

        # Local translation on Z with a parent rotated 90 degrees results in movement on X axis
        pos = node2.getWorldPosition()
        #Using fuzzyCompare due to accumulation of floating point error
        self.assertTrue(Float.fuzzyCompare(pos.x, 20, 1e-5), "{0} does not equal {1}".format(pos, Vector(20, 0, 10)))
        self.assertTrue(Float.fuzzyCompare(pos.y, 0, 1e-5), "{0} does not equal {1}".format(pos, Vector(20, 0, 10)))
        self.assertTrue(Float.fuzzyCompare(pos.z, 10, 1e-5), "{0} does not equal {1}".format(pos, Vector(20, 0, 10)))

        node2.translate(Vector(0, 0, 10), SceneNode.TransformSpace.World)

        # World translation on Z with a parent rotated 90 degrees results in movement on Z axis
        pos = node2.getWorldPosition()
        self.assertTrue(Float.fuzzyCompare(pos.x, 20, 1e-5), "{0} does not equal {1}".format(pos, Vector(20, 0, 20)))
        self.assertTrue(Float.fuzzyCompare(pos.y, 0, 1e-5), "{0} does not equal {1}".format(pos, Vector(20, 0, 20)))
        self.assertTrue(Float.fuzzyCompare(pos.z, 20, 1e-5), "{0} does not equal {1}".format(pos, Vector(20, 0, 20)))

        node1.translate(Vector(0, 0, 10))

        self.assertEqual(node1.getWorldPosition(), Vector(10, 0, 10))

        pos = node2.getWorldPosition()
        self.assertTrue(Float.fuzzyCompare(pos.x, 30, 1e-5), "{0} does not equal {1}".format(pos, Vector(30, 0, 20)))
        self.assertTrue(Float.fuzzyCompare(pos.y, 0, 1e-5), "{0} does not equal {1}".format(pos, Vector(30, 0, 20)))
        self.assertTrue(Float.fuzzyCompare(pos.z, 20, 1e-5), "{0} does not equal {1}".format(pos, Vector(30, 0, 20)))

        node1.scale(Vector(2, 2, 2))

        pos = node2.getWorldPosition()
        self.assertTrue(Float.fuzzyCompare(pos.x, 50, 1e-4), "{0} does not equal {1}".format(pos, Vector(50, 0, 30)))
        self.assertTrue(Float.fuzzyCompare(pos.y, 0, 1e-4), "{0} does not equal {1}".format(pos, Vector(50, 0, 30)))
        self.assertTrue(Float.fuzzyCompare(pos.z, 30, 1e-4), "{0} does not equal {1}".format(pos, Vector(50, 0, 30)))

        node2.translate(Vector(0, 0, 10))

        pos = node2.getWorldPosition()
        self.assertTrue(Float.fuzzyCompare(pos.x, 70, 1e-4), "{0} does not equal {1}".format(pos, Vector(70, 0, 30)))
        self.assertTrue(Float.fuzzyCompare(pos.y, 0, 1e-4), "{0} does not equal {1}".format(pos, Vector(70, 0, 30)))
        self.assertTrue(Float.fuzzyCompare(pos.z, 30, 1e-4), "{0} does not equal {1}".format(pos, Vector(70, 0, 30)))

        # World space set position
        node1 = SceneNode()
        node2 = SceneNode(node1)
        node1.setPosition(Vector(15,15,15))
        node2.setPosition(Vector(10,10,10))
        self.assertEqual(node2.getWorldPosition(), Vector(25, 25, 25))
        #node2.setPosition(Vector(15,15,15), SceneNode.TransformSpace.World)
        #self.assertEqual(node2.getWorldPosition(), Vector(15, 15, 15))
        #self.assertEqual(node2.getPosition(), Vector(0,0,0))

        node1.setPosition(Vector(15,15,15))
        node2.setPosition(Vector(0,0,0))
        node2.rotate(Quaternion.fromAngleAxis(-math.pi / 2, Vector.Unit_Y))
        node2.translate(Vector(10,0,0))
        self.assertEqual(node2.getWorldPosition(), Vector(15,15,25))

        node2.setPosition(Vector(15,15,25), SceneNode.TransformSpace.World)
        self.assertEqual(node2.getWorldPosition(), Vector(15,15,25))
        self.assertEqual(node2.getPosition(), Vector(0,0,10))




    def test_rotateWorld(self):
        pass

    def test_scaleWorld(self):
        node1 = SceneNode()
        node2 = SceneNode(node1)

        node2.scale(Vector(1.5,1.,1.))
        node2.translate(Vector(10,10,10))
        self.assertEqual(node2.getWorldPosition(), Vector(15,10,10))
        node2.scale(Vector(1.5,1,1))
        self.assertEqual(node2.getWorldPosition(), Vector(15,10,10))
        pass

if __name__ == "__main__":
    unittest.main()
