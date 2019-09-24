
from unittest.mock import patch, MagicMock
import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import TranslateTool

mocked_scene = MagicMock()

@pytest.fixture()
def translate_tool():
    application = MagicMock()
    controller = MagicMock()
    application.getController = MagicMock(return_value=controller)
    controller.getScene = MagicMock(return_value=mocked_scene)
    mocked_scene.reset_mock()
    with patch("UM.Application.Application.getInstance", MagicMock(return_value=application)):
        return TranslateTool.TranslateTool()


def test_getXYZ_no_selection(translate_tool):
    assert translate_tool.getX() == 0
    assert translate_tool.getY() == 0
    assert translate_tool.getZ() == 0

@pytest.mark.parametrize("input, result", [("12", 12),
                                           ("MONKEY", 0),
                                           ("-2", -2),
                                           ("12.6", 12.6)])
def test_parseFloat(input, result):
    assert TranslateTool.TranslateTool._parseFloat(input) == result


def test_setEnabledAxis(translate_tool):
    mock_handle = MagicMock()
    translate_tool.setHandle(mock_handle)

    translate_tool.setEnabledAxis([1, 2])

    mock_handle.setEnabledAxis.assert_called_with([1, 2])


def test_getLockPosition_no_selection(translate_tool):
    assert not translate_tool.getLockPosition()