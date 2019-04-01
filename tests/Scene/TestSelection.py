from unittest import TestCase
from unittest.mock import MagicMock

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Vector import Vector
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from UM.Operations.TranslateOperation import TranslateOperation


class TestSelection(TestCase):
    def setUp(self):
        Selection.clear()

    def tearDown(self):
        Selection.clear()

    def test_addRemoveSelection(self):
        node_1 = SceneNode()
        Selection.add(node_1)

        assert Selection.getAllSelectedObjects() == [node_1]

        Selection.remove(node_1)
        assert Selection.getAllSelectedObjects() == []

    def test_getSelectedObject(self):
        node_1 = SceneNode()
        node_2 = SceneNode()
        Selection.add(node_1)
        Selection.add(node_2)

        assert Selection.getSelectedObject(0) == node_1
        assert Selection.getSelectedObject(1) == node_2
        assert Selection.getSelectedObject(3) is None

    def test_clearSelection(self):
        node_1 = SceneNode()
        node_2 = SceneNode()
        Selection.add(node_1)
        Selection.add(node_2)
        # Ensure that the objects we want selected are selected
        assert Selection.getAllSelectedObjects() == [node_1, node_2]

        Selection.clear()
        assert Selection.getAllSelectedObjects() == []

    def test_getSelectionCenter(self):
        node_1 = SceneNode()
        node_1.getBoundingBox = MagicMock(return_value = AxisAlignedBox(Vector(0, 0, 0), Vector(10, 20, 30)))
        Selection.add(node_1)
        assert Selection.getSelectionCenter() == Vector(5, 10, 15)

        node_2 = SceneNode()
        node_2.getBoundingBox = MagicMock(return_value=AxisAlignedBox(Vector(0, 0, 0), Vector(20, 30, 40)))
        Selection.add(node_2)
        assert Selection.getSelectionCenter() == Vector(10, 15, 20)

    def test_applyOperation(self):
        # If there is no selection, nothing should happen
        assert Selection.applyOperation(TranslateOperation) is None

        node_1 = SceneNode()
        Selection.add(node_1)

        Selection.applyOperation(TranslateOperation, Vector(10, 20, 30))

        assert node_1.getPosition() == Vector(10, 20, 30)

        node_2 = SceneNode()
        Selection.add(node_2)

        assert len(Selection.applyOperation(TranslateOperation, Vector(10, 20, 30))) == 2

        # Node 1 got moved twice
        assert node_1.getPosition() == Vector(20, 40, 60)
        # And node 2 only once
        assert node_2.getPosition() == Vector(10, 20, 30)