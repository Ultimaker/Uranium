import pytest
from UM.Scene.SceneNode import SceneNode
from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from unittest.mock import MagicMock



def test_SceneNodeDecorator():
    test_node = SceneNode()
    test_decorator = SceneNodeDecorator()

    # Replace emit with mock object
    test_node.decoratorsChanged.emit = MagicMock()
    test_decorator.clear = MagicMock()

    # Nothing should happen.
    test_node.addDecorator(None)
    assert len(test_node.getDecorators()) == 0
    assert test_node.decoratorsChanged.emit.call_count == 0

    # Nothing should happen.
    test_node.addDecorator(SceneNode())
    assert len(test_node.getDecorators()) == 0
    assert test_node.decoratorsChanged.emit.call_count == 0

    # First actual change
    test_node.addDecorator(test_decorator)
    assert len(test_node.getDecorators()) == 1
    assert test_node.decoratorsChanged.emit.call_count == 1

    # Adding a decorator of the same type (SceneNodeDecorator) again should not do anything.
    test_node.addDecorator(test_decorator)
    assert len(test_node.getDecorators()) == 1
    assert test_node.decoratorsChanged.emit.call_count == 1

    # Remove the decorator again!
    test_node.removeDecorator(SceneNodeDecorator)
    assert len(test_node.getDecorators()) == 0
    assert test_node.decoratorsChanged.emit.call_count == 2
    assert test_decorator.clear.call_count == 1  # Ensure that the clear of the test decorator is called.
