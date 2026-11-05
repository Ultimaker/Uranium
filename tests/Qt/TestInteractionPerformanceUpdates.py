from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QObject

from UM.Event import Event, MouseEvent
from UM.Tool import Tool
from UM.Scene.ToolHandle import ToolHandle
from UM.Qt.Bindings.ControllerProxy import ControllerProxy


def make_proxy():
    proxy = ControllerProxy.__new__(ControllerProxy)
    QObject.__init__(proxy)
    proxy._tools_enabled = False
    proxy._property_update_timer = MagicMock()
    proxy._updateProperties = MagicMock()
    proxy._controller = MagicMock()
    return proxy


def test_drag_notifications_schedule_once_without_postponing_refresh():
    proxy = make_proxy()
    proxy._property_update_timer.isActive.side_effect = [False] + [True] * 99
    for _ in range(100):
        proxy._onPropertyChanged()
    proxy._property_update_timer.start.assert_called_once_with()
    proxy._updateProperties.assert_not_called()


def test_release_flushes_final_values():
    proxy = make_proxy()
    proxy._property_update_timer.isActive.return_value = True
    proxy._onToolOperationStopped(None)
    proxy._property_update_timer.stop.assert_called_once_with()
    proxy._updateProperties.assert_called_once_with()
    assert proxy._tools_enabled
    proxy._controller.setToolsEnabled.assert_called_once_with(True)


def test_non_drag_property_changes_remain_immediate():
    proxy = make_proxy()
    proxy._tools_enabled = True
    proxy._onPropertyChanged()
    proxy._updateProperties.assert_called_once_with()
    proxy._property_update_timer.start.assert_not_called()


@pytest.mark.parametrize("drag_plane,buttons,hit_tests", [
    (None, [], 1),
    (object(), [MouseEvent.LeftButton], 0),
    (None, [MouseEvent.RightButton], 0),
    (None, [MouseEvent.MiddleButton], 0),
])
def test_hover_readback_is_skipped_during_interaction(drag_plane, buttons, hit_tests):
    tool = Tool.__new__(Tool)
    tool._selection_pass = MagicMock()
    tool._handle = MagicMock()
    tool._drag_plane = drag_plane
    tool._locked_axis = ToolHandle.NoAxis
    event = SimpleNamespace(type=Event.MouseMoveEvent, buttons=buttons, x=0, y=0)
    with patch("UM.Scene.Selection.Selection.getFaceSelectMode", return_value=False):
        assert tool.event(event) is False
    assert tool._selection_pass.getIdAtPosition.call_count == hit_tests
