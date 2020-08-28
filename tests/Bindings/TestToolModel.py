import pytest
from unittest.mock import patch, mock_open, MagicMock

from UM.Qt.Bindings.ToolModel import ToolModel

controller = MagicMock()


@pytest.fixture
def tool_model():
    mocked_application = MagicMock()
    mocked_application.getController = MagicMock(return_value = controller)
    with patch("UM.PluginRegistry.PluginRegistry.getInstance"):
        with patch("UM.Application.Application.getInstance", MagicMock(return_value = mocked_application)):
            model = ToolModel()

    return model


def test_onToolsChanged_visible_tool(tool_model):
    tool = MagicMock(getMetaData = MagicMock(return_value = {"visible": True}))
    controller.getAllTools = MagicMock(return_value = {"beep_tool": tool})
    with patch("UM.PluginRegistry.PluginRegistry.getInstance"):
        tool_model._onToolsChanged()
    assert len(tool_model.items) == 1


def test_onToolsChanged_invisible_tool(tool_model):
    tool = MagicMock(getMetaData=MagicMock(return_value={"visible": False}))
    controller.getAllTools = MagicMock(return_value={"beep_tool": tool})
    with patch("UM.PluginRegistry.PluginRegistry.getInstance"):
        tool_model._onToolsChanged()
    assert len(tool_model.items) == 0