
from unittest.mock import patch, MagicMock
import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import RotateTool

mocked_scene = MagicMock()

@pytest.fixture()
def rotate_tool():
    application = MagicMock()
    controller = MagicMock()
    application.getController = MagicMock(return_value=controller)
    controller.getScene = MagicMock(return_value=mocked_scene)
    mocked_scene.reset_mock()
    with patch("UM.Application.Application.getInstance", MagicMock(return_value=application)):
        return RotateTool.RotateTool()


@pytest.mark.parametrize("data", [
    {"attribute": "rotationSnapAngle", "value": 32},
    {"attribute": "rotationSnap", "value": False},
])
def test_getAndSet(data, rotate_tool):
    # Convert the first letter into a capital
    attribute = list(data["attribute"])
    attribute[0] = attribute[0].capitalize()
    attribute = "".join(attribute)

    # mock the correct emit
    rotate_tool.propertyChanged = MagicMock()

    # Attempt to set the value
    getattr(rotate_tool, "set" + attribute)(data["value"])

    # Check if signal fired.
    assert rotate_tool.propertyChanged.emit.call_count == 1

    # Ensure that the value got set
    assert getattr(rotate_tool, "get" + attribute)() == data["value"]

    # Attempt to set the value again
    getattr(rotate_tool, "set" + attribute)(data["value"])
    # The signal should not fire again
    assert rotate_tool.propertyChanged.emit.call_count == 1