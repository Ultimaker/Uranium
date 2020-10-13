# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from unittest.mock import patch

import pytest

from UM.Math.Plane import Plane
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool


def createTool(tool_id):
    with patch("UM.Application.Application.getInstance"):
        result = Tool()
    result.setPluginId(tool_id)
    return result


def test_exposedProperties():
    test_tool_1 = createTool("test_tool_1")

    test_tool_1.setExposedProperties("bla", "omg", "zomg")
    assert test_tool_1.getExposedProperties() == ["bla", "omg", "zomg"]


test_validate_data = [
    {"attribute": "DragPlane", "value": Plane()},
    {"attribute": "Handle", "value": None}
]


@pytest.mark.parametrize("data", test_validate_data)
def test_getAndSet(data):
    test_tool = createTool("whatever")
    # Attempt to set the value
    getattr(test_tool, "set" + data["attribute"])(data["value"])

    # Ensure that the value got set
    assert getattr(test_tool, "get" + data["attribute"])() == data["value"]


def test_toolEnabledChanged():
    test_tool_1 = createTool("test_tool_1")
    assert test_tool_1.getEnabled()

    # Fake the signal from the controller
    test_tool_1._onToolEnabledChanged("SomeOtherTOol", True)
    assert test_tool_1.getEnabled()
    # Fake the signal from the controller, but this time it's a signal that should force the tool to change.
    test_tool_1._onToolEnabledChanged("test_tool_1", False)
    assert not test_tool_1.getEnabled()


def test_getShortcutKey():
    test_tool_1 = createTool("whatever!")
    # Test coverage is magic. It should be None by default.
    assert test_tool_1.getShortcutKey() is None


def test_getDragVector():
    test_tool_1 = createTool("test_tool_1")

    # No drag plane set
    assert test_tool_1.getDragVector(0, 0) is None
    test_tool_1.setDragPlane(Plane())
    # No drag start
    assert test_tool_1.getDragVector(0, 0) is None


def test_getDragStart():
    test_tool_1 = createTool("whatever")
    # Test coverage is magic. It should be None by default.
    assert test_tool_1.getDragStart() is None


def test_getController():
    test_tool_1 = createTool("whatever")
    # Test coverage is magic. It should not be None by default, since the application provided one
    assert test_tool_1.getController() is not None


def test_setLockedAxis():
    test_tool_1 = createTool("whatever")
    with patch("UM.Application.Application.getInstance"):
        test_tool_handle_1 = ToolHandle()
    test_tool_handle_1._enabled = True
    test_tool_handle_1._auto_scale = False
    # Pretend like the toolhandle actually got rendered at least once
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
        with patch("UM.Resources.Resources.getPath"):
            test_tool_handle_1.render(None)

    # Needs to start out with Nothing locked
    assert test_tool_1.getLockedAxis() == ToolHandle.NoAxis

    # Just the vanilla changing.
    test_tool_1.setLockedAxis(ToolHandle.XAxis)
    assert test_tool_1.getLockedAxis() == ToolHandle.XAxis

    test_tool_1.setHandle(test_tool_handle_1)
    test_tool_1.setLockedAxis(ToolHandle.YAxis)
    assert test_tool_1.getLockedAxis() == ToolHandle.YAxis
    assert test_tool_handle_1.getActiveAxis() == ToolHandle.YAxis


def test_getSelectedObjectsWithoutSelectedAncestors():
    scene_node_1 = SceneNode()
    Selection.add(scene_node_1)
    test_tool_1 = createTool("whatever")
    assert test_tool_1._getSelectedObjectsWithoutSelectedAncestors() == [scene_node_1]


