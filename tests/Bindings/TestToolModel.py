import pytest
from unittest.mock import patch, mock_open, MagicMock

from UM.Qt.Bindings.ToolModel import ToolModel

controller = MagicMock()

@pytest.fixture
def tool_model():
    mocked_application = MagicMock()
    mocked_application.getController = MagicMock(return_value = controller)

    with patch("UM.Application.Application.getInstance", MagicMock(return_value = mocked_application)):
        model = ToolModel()

    return model


def test_onToolsChanged_visible_tool(tool_model):
    controller.getAllTools = MagicMock(return_value = ["beep_tool"])
    registry = MagicMock()
    registry.getMetaData = MagicMock(return_value = {"tool": {"visible": True}})
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value=registry)):
        tool_model._onToolsChanged()
    assert len(tool_model.items) == 1

def test_onToolsChanged_invisible_tool(tool_model):
    controller.getAllTools = MagicMock(return_value = ["beep_tool"])
    registry = MagicMock()
    registry.getMetaData = MagicMock(return_value = {"tool": {"visible": False}})
    with patch("UM.PluginRegistry.PluginRegistry.getInstance", MagicMock(return_value=registry)):
        tool_model._onToolsChanged()
    assert len(tool_model.items) == 0