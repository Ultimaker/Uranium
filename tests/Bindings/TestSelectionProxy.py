from unittest import TestCase
from unittest.mock import MagicMock

from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Vector import Vector
from UM.Qt.Bindings.SelectionProxy import SelectionProxy
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from UM.Operations.TranslateOperation import TranslateOperation


class TestSelectionProxy(TestCase):

    def setUp(self):
        Selection.clear()
        self.proxy = SelectionProxy()

    def tearDown(self):
        Selection.clear()

    def test_hasSelection(self):
        # Nothing is selected by default
        assert not self.proxy.hasSelection

        node_1 = SceneNode()
        Selection.add(node_1)

        assert self.proxy.hasSelection

        Selection.remove(node_1)
        assert not self.proxy.hasSelection

    def test_selectionCount(self):
        assert self.proxy.selectionCount == 0

        node_1 = SceneNode()
        Selection.add(node_1)
        assert self.proxy.selectionCount == 1

        node_2 = SceneNode()
        Selection.add(node_2)
        assert self.proxy.selectionCount == 2

    def test_selectionNames(self):
        node_1 = SceneNode(name="TestNode1")
        node_2 = SceneNode(name="TestNode2")
        Selection.add(node_2)
        Selection.add(node_1)
        assert self.proxy.selectionNames == ["TestNode2", "TestNode1"]

