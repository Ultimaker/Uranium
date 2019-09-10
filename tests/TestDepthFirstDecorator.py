from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.SceneNode import SceneNode


def test_DepthFirstIterator():

    root_node = SceneNode()

    node_1 = SceneNode()
    root_node.addChild(node_1)

    node_1_child_1 = SceneNode()
    node_1_child_2 = SceneNode()

    node_1.addChild(node_1_child_1)
    node_1.addChild(node_1_child_2)

    node_2 = SceneNode()
    root_node.addChild(node_2)

    node_2_child_1 = SceneNode()
    node_2.addChild(node_2_child_1)

    assert list(DepthFirstIterator(root_node)) == [root_node, node_1, node_2, node_1_child_1, node_1_child_2, node_2_child_1]