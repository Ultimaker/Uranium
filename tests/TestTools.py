# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from unittest.mock import MagicMock, patch
from UM.Application import Application

from UM.Controller import Controller
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool


def test_addTools(application):
    controller = Controller(application)

    # Switch out the emits with a mock.
    controller.toolsChanged.emit = MagicMock()
    controller.activeToolChanged.emit = MagicMock()
    controller.toolOperationStarted.emit = MagicMock()
    controller.toolOperationStopped.emit = MagicMock()

    test_tool_1 = Tool()
    test_tool_1.setPluginId("test_tool_1")

    test_tool_2 = Tool()
    test_tool_2.setPluginId("test_tool_2")

    controller.addTool(test_tool_1)
    assert controller.toolsChanged.emit.call_count == 1

    controller.addTool(test_tool_2)
    assert controller.toolsChanged.emit.call_count == 2

    controller.addTool(test_tool_1)
    assert controller.toolsChanged.emit.call_count == 2
    assert len(controller.getAllTools()) == 2

    # Set active tool with an unknown name.
    controller.setActiveTool("nope nope!")
    assert controller.getActiveTool() is None
    assert controller.activeToolChanged.emit.call_count == 0

    # Set active tool by reference
    controller.setActiveTool(test_tool_1)
    assert controller.getActiveTool() == test_tool_1
    assert controller.activeToolChanged.emit.call_count == 1

    # Set active tool by ID, but the same as is already active.
    controller.setActiveTool("test_tool_1")
    assert controller.getActiveTool() == test_tool_1
    assert controller.activeToolChanged.emit.call_count == 1

    # Set active tool by ID
    controller.setActiveTool("test_tool_2")
    assert controller.getActiveTool() == test_tool_2
    assert controller.activeToolChanged.emit.call_count == 2

    assert controller.getTool("ZOMG") is None
    assert controller.getTool("test_tool_1") == test_tool_1
    assert controller.getTool("test_tool_2") == test_tool_2


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
