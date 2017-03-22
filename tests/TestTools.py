# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from unittest.mock import MagicMock
from UM.Application import Application

from UM.Controller import Controller
from UM.Tool import Tool


def test_tools():
    mock_application = MagicMock()

    Application.getInstance = MagicMock(return_type = mock_application)
    controller = Controller(mock_application)

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

    # Set if with an unknown name.
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









