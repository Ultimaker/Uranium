
from unittest.mock import patch, MagicMock
import sys
import os

from UM.Math.AxisAlignedBox import AxisAlignedBox

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from UM.Math.Vector import Vector
import ScaleTool
import pytest

mocked_scene = MagicMock()


@pytest.fixture()
def scale_tool():
    application = MagicMock()
    controller = MagicMock()
    application.getController = MagicMock(return_value=controller)
    controller.getScene = MagicMock(return_value=mocked_scene)
    mocked_scene.reset_mock()
    with patch("UM.Application.Application.getInstance", MagicMock(return_value=application)):
        return ScaleTool.ScaleTool()


@pytest.mark.parametrize("data", [
    {"attribute": "nonUniformScale", "value": True},
    {"attribute": "scaleSnap", "value": True},
])
def test_getAndSet(data, scale_tool):
    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # mock the correct emit
    scale_tool.propertyChanged = MagicMock()

    # Attempt to set the value
    getattr(scale_tool, "set" + attribute)(data["value"])

    # Check if signal fired.
    assert scale_tool.propertyChanged.emit.call_count == 1

    # Ensure that the value got set
    assert getattr(scale_tool, "get" + attribute)() == data["value"]

    # Attempt to set the value again
    getattr(scale_tool, "set" + attribute)(data["value"])
    # The signal should not fire again
    assert scale_tool.propertyChanged.emit.call_count == 1


def createMockedSelectionWithBoundingBox(min_size, max_size):
    selection = MagicMock()
    node = MagicMock()
    binding_box = AxisAlignedBox(min_size, max_size)
    node.getBoundingBox = MagicMock(return_value=binding_box)
    selection.hasSelection = MagicMock(return_value=True)
    selection.getSelectedObject = MagicMock(return_value=node)
    return selection

def createMockedSelectionWithScale(scale):
    selection = MagicMock()
    node = MagicMock()
    node.getScale = MagicMock(return_value=scale)
    selection.hasSelection = MagicMock(return_value=True)
    selection.getSelectedObject = MagicMock(return_value=node)
    return selection


def test_objectWidthDepthHeight(scale_tool):
    selection = createMockedSelectionWithBoundingBox(Vector(0, 0, 0), Vector(10, 20, 30))
    with patch("ScaleTool.Selection", selection):
        assert scale_tool.getObjectWidth() == 10
        assert scale_tool.getObjectHeight() == 20
        assert scale_tool.getObjectDepth() == 30


def test_objectWidthDepthHeight_noSelection(scale_tool):
    # If no object is selected, we should get some sane defaults.
    selection = MagicMock()
    selection.hasSelection = MagicMock(return_value = False)
    selection.getSelectedObject = MagicMock(return_value = None)
    with patch("ScaleTool.Selection", selection):
        assert scale_tool.getObjectWidth() == 0
        assert scale_tool.getObjectHeight() == 0
        assert scale_tool.getObjectDepth() == 0


def test_objectSize(scale_tool):
    selection = createMockedSelectionWithScale(Vector(2, 3, 4))
    with patch("ScaleTool.Selection", selection):
        assert scale_tool.getScaleX() == 2.0
        assert scale_tool.getScaleY() == 3.0
        assert scale_tool.getScaleZ() == 4.0


def test_objectSize_noSelection(scale_tool):
    # If no object is selected, we should get some sane defaults.
    selection = MagicMock()
    selection.hasSelection = MagicMock(return_value=False)
    with patch("ScaleTool.Selection", selection):
        assert scale_tool.getScaleX() == 1.0
        assert scale_tool.getScaleY() == 1.0
        assert scale_tool.getScaleZ() == 1.0


def test_setObjectWidth(scale_tool):
    selection = createMockedSelectionWithBoundingBox(Vector(0, 0, 0), Vector(10, 10, 10))

    scale_tool._scaleSelectedNodes = MagicMock() # Not the function under test, so isolate it.
    with patch("ScaleTool.Selection", selection):
        scale_tool.setObjectWidth(40)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(4, 4, 4))

    # Now try again with non-uniform scaling
    scale_tool._scaleSelectedNodes.reset_mock()
    with patch("ScaleTool.Selection", selection):
        scale_tool.setNonUniformScale(True)
        scale_tool.setObjectWidth(40)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(4, 1, 1))


def test_setObjectHeight(scale_tool):
    selection = createMockedSelectionWithBoundingBox(Vector(0, 0, 0), Vector(20, 20, 20))

    scale_tool._scaleSelectedNodes = MagicMock() # Not the function under test, so isolate it.
    with patch("ScaleTool.Selection", selection):
        scale_tool.setObjectHeight(40)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(2, 2, 2))

    # Now try again with non-uniform scaling
    scale_tool._scaleSelectedNodes.reset_mock()
    with patch("ScaleTool.Selection", selection):
        scale_tool.setNonUniformScale(True)
        scale_tool.setObjectHeight(40)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(1, 2, 1))


def test_setObjectDepth(scale_tool):
    selection = createMockedSelectionWithBoundingBox(Vector(0, 0, 0), Vector(30, 30, 30))

    scale_tool._scaleSelectedNodes = MagicMock() # Not the function under test, so isolate it.
    with patch("ScaleTool.Selection", selection):
        scale_tool.setObjectDepth(90)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(3, 3, 3))

    # Now try again with non-uniform scaling
    scale_tool._scaleSelectedNodes.reset_mock()
    with patch("ScaleTool.Selection", selection):
        scale_tool.setNonUniformScale(True)
        scale_tool.setObjectDepth(90)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(1, 1, 3))


def test_setScaleX(scale_tool):
    selection = createMockedSelectionWithScale(Vector(1, 1, 1))

    scale_tool._scaleSelectedNodes = MagicMock()  # Not the function under test, so isolate it.
    with patch("ScaleTool.Selection", selection):
        scale_tool.setScaleX(90)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(90, 90, 90))

    # Now try again with non-uniform scaling
    scale_tool._scaleSelectedNodes.reset_mock()
    with patch("ScaleTool.Selection", selection):
        scale_tool.setNonUniformScale(True)
        scale_tool.setScaleX(90)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(90, 1, 1))


def test_setScaleY(scale_tool):
    selection = createMockedSelectionWithScale(Vector(10, 10, 10))

    scale_tool._scaleSelectedNodes = MagicMock()  # Not the function under test, so isolate it.
    with patch("ScaleTool.Selection", selection):
        scale_tool.setScaleY(20)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(2, 2, 2))

    # Now try again with non-uniform scaling
    scale_tool._scaleSelectedNodes.reset_mock()
    with patch("ScaleTool.Selection", selection):
        scale_tool.setNonUniformScale(True)
        scale_tool.setScaleY(20)

    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(1, 2, 1))


def test_setScaleZ(scale_tool):
    selection = createMockedSelectionWithScale(Vector(10, 10, 10))

    scale_tool._scaleSelectedNodes = MagicMock()  # Not the function under test, so isolate it.
    with patch("ScaleTool.Selection", selection):
        scale_tool.setScaleZ(5)
    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(0.5, 0.5, 0.5))

    # Now try again with non-uniform scaling
    scale_tool._scaleSelectedNodes.reset_mock()
    with patch("ScaleTool.Selection", selection):
        scale_tool.setNonUniformScale(True)
        scale_tool.setScaleZ(5)

    scale_tool._scaleSelectedNodes.assert_called_once_with(Vector(1, 1, 0.5))

