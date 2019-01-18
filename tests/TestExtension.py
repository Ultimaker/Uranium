from unittest.mock import MagicMock

from UM.Extension import Extension


def test_activateMenuItem():
    test_extension = Extension()
    mock_object = MagicMock()
    mock_function = mock_object.bla
    test_extension.addMenuItem("test", mock_function)
    test_extension.activateMenuItem("test")

    # Check that the function was called without any attributes being passed along.
    mock_function.assert_called_once_with()


def test_menuItemOrder():
    test_extension = Extension()

    test_extension.addMenuItem("b", MagicMock())
    test_extension.addMenuItem("a", MagicMock())

    # Ensure that the order by which the menu items were added is the same.
    assert test_extension.getMenuItemList() == ["b", "a"]


# Super simple test, there is no reason this should ever change, but now extension is 100% tested
def test_menuName():
    test_extension = Extension()
    assert test_extension.getMenuName() is None
    test_extension.setMenuName("bloop")
    assert test_extension.getMenuName() == "bloop"
