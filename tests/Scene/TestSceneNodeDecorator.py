import pytest
from UM.Scene.SceneNode import SceneNode
from UM.Scene.SceneNodeDecorator import SceneNodeDecorator
from unittest.mock import MagicMock


class TheAmazingTestDecorator(SceneNodeDecorator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def theAmazingDecoration(self):
        return "Amazing!"

    def theEvenMoreAmazingDecoration(self, test, more_test ="Wow", much_test ="so wow"):
        return test, more_test, much_test


class TheLessAmazingTestDecorator(SceneNodeDecorator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def theAmazingDecoration(self):
        return "amazing"


class TheNotSoAmazingTestDecorator(SceneNodeDecorator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def theOkayDecoration(self):
        return "okayish"


if __name__ == '__main__':
    def test_SceneNodeDecorator():
        test_node = SceneNode()
        test_decorator = SceneNodeDecorator()
        amazing_decorator = TheAmazingTestDecorator()
        less_amazing_decorator = TheLessAmazingTestDecorator()
        not_amazing_decorator = TheNotSoAmazingTestDecorator()

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

        # Add a number of decorators!
        test_node.addDecorator(amazing_decorator)
        test_node.addDecorator(less_amazing_decorator)
        test_node.addDecorator(not_amazing_decorator)
        assert test_node.decoratorsChanged.emit.call_count == 5
        assert len(test_node.getDecorators()) == 3

        assert test_node.hasDecoration("zomg") == False
        assert test_node.hasDecoration("theOkayDecoration")
        assert test_node.hasDecoration("theAmazingDecoration")

        # Calling the decorations with args / kwargs
        assert test_node.callDecoration("theOkayDecoration", None) is None
        assert test_node.callDecoration("theEvenMoreAmazingDecoration", "beep") == ("beep", "Wow", "so wow")
        assert test_node.callDecoration("theEvenMoreAmazingDecoration", "beep", much_test = "Wow") == ("beep", "Wow", "Wow")

        # Calling decoration that is "double"
        assert test_node.callDecoration("theAmazingDecoration") == "Amazing!"
        test_node.removeDecorator(TheAmazingTestDecorator)
        assert test_node.callDecoration("theAmazingDecoration") == "amazing"

        not_amazing_decorator.clear = MagicMock()
        test_node.removeDecorators()
        # Also assure that removing all decorators also triggers the clear
        assert not_amazing_decorator.clear.call_count == 1
        assert len(test_node.getDecorators()) == 0
        assert test_node.decoratorsChanged.emit.call_count == 8  # +3 changes

