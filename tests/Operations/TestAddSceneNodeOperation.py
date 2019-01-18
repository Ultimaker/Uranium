from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection


def test_SimpleRedoUndo():
    node = SceneNode()
    parent_node = SceneNode()
    operation = AddSceneNodeOperation(node, parent_node)
    operation.redo()

    assert node.getParent() == parent_node

    operation.undo()

    assert node.getParent() is None


def test_UndoRedoWithSelection():
    node = SceneNode()
    parent_node = SceneNode()
    Selection.add(node)

    operation = AddSceneNodeOperation(node, parent_node)
    operation.undo()

    assert not Selection.isSelected(node)

    operation.redo()
    assert Selection.isSelected(node)
