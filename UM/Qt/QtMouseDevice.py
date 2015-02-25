from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtGui import QMouseEvent

from UM.InputDevice import InputDevice
from UM.Event import MouseEvent, WheelEvent

##  An InputDevice subclass that processes Qt mouse events and returns a UM.Event.MouseEvent
class QtMouseDevice(InputDevice):
    def __init__(self, window):
        super().__init__()
        self._x = None
        self._y = None
        self._window = window

    def handleEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            ex, ey = self._normalizeCoordinates(event.x(), event.y())
            e = MouseEvent(MouseEvent.MousePressEvent, ex, ey, self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = ex
            self._y = ey
            self.event.emit(e)
        elif event.type() == QEvent.MouseMove:
            ex, ey = self._normalizeCoordinates(event.x(), event.y())
            e = MouseEvent(MouseEvent.MouseMoveEvent, ex, ey, self._x, self._y, self._qtButtonsToButtonList(event.buttons()))
            self._x = ex
            self._y = ey
            self.event.emit(e)
        elif event.type() == QEvent.MouseButtonRelease:
            ex, ey = self._normalizeCoordinates(event.x(), event.y())
            e = MouseEvent(MouseEvent.MouseReleaseEvent, ex, ey, self._x, self._y, self._qtButtonsToButtonList(event.button()))
            self._x = ex
            self._y = ey
            self.event.emit(e)
        elif event.type() == QEvent.Wheel:
            delta = event.angleDelta()
            e = WheelEvent(delta.x(), delta.y())
            self.event.emit(e)

    def _qtButtonsToButtonList(self, qtButtons):
        buttons = []

        if qtButtons & Qt.LeftButton:
            buttons.append(MouseEvent.LeftButton)
        if qtButtons & Qt.RightButton:
            buttons.append(MouseEvent.RightButton)
        if qtButtons & Qt.MiddleButton:
            buttons.append(MouseEvent.MiddleButton)

        return buttons

    def _normalizeCoordinates(self, x, y):
        nx = 2.0 * (x / self._window.width()) - 1.0
        ny = 2.0 * (y / self._window.height()) - 1.0

        return nx, ny
