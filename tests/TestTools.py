# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from unittest.mock import patch
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool


def test_exposedProperties():

    test_tool_1 = Tool()
    test_tool_1.setPluginId("test_tool_1")

    test_tool_1.setExposedProperties("bla", "omg", "zomg")
    assert test_tool_1.getExposedProperties() == ["bla", "omg", "zomg"]


def test_setLockedAxis():
    test_tool_1 = Tool()
    test_tool_handle_1 = ToolHandle()
    test_tool_handle_1._auto_scale = False
    # Pretend like the toolhandle actually got rendered at least once
    with patch("UM.View.GL.OpenGL.OpenGL.getInstance"):
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
