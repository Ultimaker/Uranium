# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData
from UM.Scene.GroupDecorator import GroupDecorator
from UM.Scene.SceneNode import SceneNode

from UM.Math.Vector import Vector
from UM.Math.Quaternion import Quaternion
from UM.Math.Matrix import Matrix
from UM.Math.Float import Float

import unittest
import math

from copy import deepcopy
from unittest.mock import MagicMock

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

        node_orientation = deepcopy(node.getOrientation())
        node_orientation.normalize() #For fair comparison.
        self.assertEqual(node_orientation, Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node.setOrientation(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node_orientation = deepcopy(node.getOrientation())
        node_orientation.normalize() #For fair comparison.
        self.assertEqual(node_orientation, Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

    def test_rotate(self):
        node = SceneNode()

        self.assertEqual(node.getOrientation(), Quaternion())

        node.rotate(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node_orientation = deepcopy(node.getOrientation())
        node_orientation.normalize() #For fair comparison.
        self.assertEqual(node_orientation, Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node.rotate(Quaternion.fromAngleAxis(math.pi / 4, Vector.Unit_Z))

        node_orientation = deepcopy(node.getOrientation())
        node_orientation.normalize()
        self.assertEqual(node_orientation, Quaternion.fromAngleAxis(math.pi / 2, Vector.Unit_Z))

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

    def test_setName(self):
        node = SceneNode()
        node.setName("DERP")
        assert node.getName() == "DERP"

    def test_getDepth(self):
        node1 = SceneNode()
        node2 = SceneNode()
        node3 = SceneNode()
        node4 = SceneNode()

        node1.addChild(node2)
        node1.addChild(node3)
        node2.addChild(node4)

        assert node1.getDepth() == 0
        assert node2.getDepth() == 1
        assert node3.getDepth() == 1
        assert node4.getDepth() == 2

    def test_visibility(self):
        node1 = SceneNode()
        node1.setVisible(True)
        assert node1.isVisible()

        node2 = SceneNode()
        node1.addChild(node2)
        node2.setVisible(True)
        assert node2.isVisible()

        node1.setVisible(False)
        assert not node1.isVisible()
        assert not node2.isVisible()

    def test_enabled(self):
        node1 = SceneNode()
        node1.setEnabled(True)
        assert node1.isEnabled()

        node2 = SceneNode()
        node1.addChild(node2)
        node2.setEnabled(True)
        assert node2.isEnabled()

        node1.setEnabled(False)
        assert not node1.isEnabled()
        assert not node2.isEnabled()

    def test_removeChildren(self):
        node1 = SceneNode()
        node2 = SceneNode()
        node1.addChild(node2)
        assert node1.hasChildren()

        node1.removeAllChildren()

        assert not node1.hasChildren()

    def test_getAllChildren(self):
        parent_node = SceneNode()
        child_node_1 = SceneNode()
        child_node_2 = SceneNode()
        parent_node.addChild(child_node_1)
        parent_node.addChild(child_node_2)

        child_1_of_child_node_1 = SceneNode()
        child_2_of_child_node_1 = SceneNode()
        child_node_1.addChild(child_1_of_child_node_1)
        child_node_1.addChild(child_2_of_child_node_1)

        child_1_of_child_node_2 = SceneNode()
        child_node_2.addChild(child_1_of_child_node_2)

        assert parent_node.getAllChildren() == [child_node_1, child_node_2, child_1_of_child_node_1, child_2_of_child_node_1, child_1_of_child_node_2]

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

    def test_deepCopy(self):
        node_1 = SceneNode()
        node_2 = SceneNode()
        node_1.translate(Vector(1, 2, 3))
        node_1.scale(Vector(1.5, 1., 1.))
        node_1.setMeshData(MeshData())
        node_1.addChild(node_2)
        node_1.addDecorator(GroupDecorator())
        copied_node = deepcopy(node_1)

        assert copied_node.getScale() == Vector(1.5, 1, 1)
        assert copied_node.getPosition() == Vector(1, 2, 3)
        assert len(copied_node.getChildren()) == 1
        # Ensure that the decorator also got copied
        assert copied_node.callDecoration("isGroup")

    def test_addRemoveDouble(self):
        # Adding a child that's already a child of a node should not cause issues. Same for trying to remove one that isn't a child

        node_1 = SceneNode()
        node_2 = SceneNode()
        # Should work
        node_1.addChild(node_2)
        # Should still work!
        node_1.addChild(node_2)

        # This has already been tested somewhere else, so no problems are expected
        node_1.removeChild(node_2)
        # Doing it again shouldn't break.
        node_1.removeChild(node_2)

    def test_getSetMeshdata(self):
        node = SceneNode()
        test_mesh = MeshData()
        node.setMeshData(test_mesh)
        assert node.getMeshData() == test_mesh

    def test_getTransformedMeshdata(self):
        node = SceneNode()
        node.translate(Vector(10, 0 , 0))
        builder = MeshBuilder()
        builder.addVertex(10, 20, 20)
        node.setMeshData(builder.build())

        transformed_mesh = node.getMeshDataTransformed()

        transformed_vertex = transformed_mesh.getVertices()[0]
        assert transformed_vertex[0] == 20
        assert transformed_vertex[1] == 20
        assert transformed_vertex[2] == 20

    def test_getSetSetting(self):
        node = SceneNode()
        node.setSetting("ZOMG", "BEEP")
        assert node.getSetting("ZOMG") == "BEEP"
        assert node.getSetting("unknown") == ""
        assert node.getSetting("unknown", "zomg") == "zomg"

    def test_getSetSelectable(self):
        node = SceneNode()
        node.setSelectable(True)
        assert node.isSelectable()
        node.setEnabled(False)
        assert not node.isSelectable() # Node is disabled, can't select it anymore

    def test_getSetMirror(self):
        node = SceneNode()
        node.setMirror(Vector(-1, 1, 1))
        assert node.getMirror() == Vector(-1, 1, 1)

    def test_setCenterPosition(self):
        node = SceneNode()
        child_node = SceneNode()
        node.addChild(child_node)
        child_node.setCenterPosition = MagicMock()

        builder = MeshBuilder()
        builder.addVertex(10, 20, 20)
        node.setMeshData(builder.build())

        node.setCenterPosition(Vector(-10, 0, 0))

        transformed_mesh = node.getMeshData()

        transformed_vertex = transformed_mesh.getVertices()[0]
        assert transformed_vertex[0] == 20
        assert transformed_vertex[1] == 20
        assert transformed_vertex[2] == 20

        child_node.setCenterPosition.assert_called_once_with(Vector(-10, 0, 0))


if __name__ == "__main__":
    unittest.main()
