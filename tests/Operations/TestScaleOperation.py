from UM.Math.Vector import Vector
from UM.Operations.ScaleOperation import ScaleOperation
from UM.Scene.SceneNode import SceneNode


def test_setSimpleScale():
    node = SceneNode()
    op = ScaleOperation(node, Vector(1, 2, 3), set_scale = True)

    op.redo()
    assert node.getScale() == Vector(1, 2, 3)

    op.undo()
    assert node.getScale() == Vector(1, 1, 1)


def test_addScale():
    node = SceneNode()
    op = ScaleOperation(node, Vector(1, 2, 3), set_scale = True)
    op.redo()

    op2 = ScaleOperation(node, Vector(1, 2, 3), add_scale = True)
    op2.redo()
    assert node.getScale() == Vector(2, 4, 6)


def test_relativeScale():
    node = SceneNode()
    op = ScaleOperation(node, Vector(2, 2, 2), set_scale=True)
    op.redo()

    op2 = ScaleOperation(node, Vector(1, 2, 3), relative_scale=True)
    op2.redo()
    assert node.getScale() == Vector(3, 4, 5)
