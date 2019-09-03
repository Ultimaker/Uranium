
from unittest.mock import patch, MagicMock
import sys
import os

from UM.Event import MouseEvent

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from UM.Math.Vector import Vector
import CameraTool
import pytest


mocked_scene = MagicMock()


def generateMouseEvent(left: bool, middle: bool, right: bool):
    event = MagicMock()
    event.buttons = []
    if left:
        event.buttons.append(MouseEvent.LeftButton)
    if middle:
        event.buttons.append(MouseEvent.MiddleButton)
    if right:
        event.buttons.append(MouseEvent.RightButton)
    return event


@pytest.fixture()
def camera_tool():
    application = MagicMock()
    controller = MagicMock()
    application.getController = MagicMock(return_value = controller)
    controller.getScene = MagicMock(return_value = mocked_scene)
    mocked_scene.reset_mock()
    with patch("UM.Application.Application.getInstance", MagicMock(return_value = application)):
        return CameraTool.CameraTool()


def test_setOrigin(camera_tool):
    # Isolation, we just want to know it gets called with the right data.
    camera_tool._rotateCamera = MagicMock()
    camera_tool.setOrigin(Vector(1, 2, 3))

    assert camera_tool.getOrigin() == Vector(1, 2, 3)
    camera_tool._rotateCamera.assert_called_with(0, 0)


@pytest.mark.parametrize("event, result", [(generateMouseEvent(True, False, False), False),
                                           (generateMouseEvent(False, True, False), True),
                                           (generateMouseEvent(False, False, True), False),
                                           (generateMouseEvent(True, False, True), False),
                                           (generateMouseEvent(False, False, False), False),
                                           ])
def test_moveEvent(camera_tool, event, result):
    assert camera_tool.moveEvent(event) == result


@pytest.mark.parametrize("event, result", [(generateMouseEvent(True, False, False), True),
                                           (generateMouseEvent(False, True, False), True),
                                           (generateMouseEvent(False, False, True), True),
                                           (generateMouseEvent(True, False, True), True),
                                           (generateMouseEvent(False, False, False), False),  # Only the no button pressed case should be false
                                           ])
def test_moveEventShiftActive(camera_tool, event, result):
    camera_tool._shift_is_active = True
    assert camera_tool.moveEvent(event) == result

