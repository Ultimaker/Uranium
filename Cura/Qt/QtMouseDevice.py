from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QMouseEvent

from Cura.InputDevice import InputDevice
from Cura.Event import MouseEvent

class QtMouseDevice(InputDevice):
    def __init__(self):
        super().__init__()
        self._x = None
        self._y = None

    def handleEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            e = MouseEvent(MouseEvent.MousePressEvent, event.x(), event.y(), self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = event.x()
            self._y = event.y()
            return e
        elif event.type() == QEvent.MouseMove:
            e = MouseEvent(MouseEvent.MouseMoveEvent, event.x(), event.y(), self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = event.x()
            self._y = event.y()
            return e
        elif event.type() == QEvent.MouseButtonRelease:
            e = MouseEvent(MouseEvent.MouseReleaseEvent, event.x(), event.y(), self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = event.x()
            self._y = event.y()
            return e

        return None

    def _qtButtonsToButtonList(self, qtButtons):
        buttons = []

        if qtButtons & Qt.LeftButton:
            buttons.append(MouseEvent.LeftButton)
        if qtButtons & Qt.RightButton:
            buttons.append(MouseEvent.RightButton)
        if qtButtons & Qt.MiddleButton:
            buttons.append(MouseEvent.MiddleButton)

        return buttons
