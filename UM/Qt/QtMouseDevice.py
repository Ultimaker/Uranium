# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import Qt, QEvent

from UM.InputDevice import InputDevice
from UM.Event import MouseEvent, WheelEvent


class QtMouseDevice(InputDevice):
    """An InputDevice subclass that processes Qt mouse events and returns a UM.Event.MouseEvent"""

    def __init__(self, window):
        super().__init__()
        self._x = None
        self._y = None
        self._window = window

    def handleEvent(self, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            ex, ey = self._normalizeCoordinates(event.pos().x(), event.pos().y())
            e = MouseEvent(MouseEvent.MousePressEvent, ex, ey, self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = ex
            self._y = ey
            self.event.emit(e)
        elif event.type() == QEvent.Type.MouseMove:
            ex, ey = self._normalizeCoordinates(event.pos().x(), event.pos().y())
            e = MouseEvent(MouseEvent.MouseMoveEvent, ex, ey, self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = ex
            self._y = ey
            self.event.emit(e)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            ex, ey = self._normalizeCoordinates(event.pos().x(), event.pos().y())
            e = MouseEvent(MouseEvent.MouseReleaseEvent, ex, ey, self._x, self._y, self._qtButtonsToButtonList(event.button()))
            self._x = ex
            self._y = ey
            self.event.emit(e)
        elif event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta()
            e = WheelEvent(delta.x(), delta.y())
            self.event.emit(e)

    def _qtButtonsToButtonList(self, qt_buttons):
        buttons = []

        if qt_buttons == Qt.MouseButton.LeftButton.value:
            buttons.append(MouseEvent.LeftButton)
        if qt_buttons == Qt.MouseButton.RightButton.value:
            buttons.append(MouseEvent.RightButton)
        if qt_buttons == Qt.MouseButton.MiddleButton.value:
            buttons.append(MouseEvent.MiddleButton)
        return buttons

    def _normalizeCoordinates(self, x, y):
        try:
            nx = 2.0 * (x / self._window.width()) - 1.0
            ny = 2.0 * (y / self._window.height()) - 1.0
        except ZeroDivisionError:
            return 0, 0

        return nx, ny
