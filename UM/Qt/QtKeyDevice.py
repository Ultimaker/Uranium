# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import Qt, QEvent

from UM.InputDevice import InputDevice
from UM.Event import KeyEvent


class QtKeyDevice(InputDevice):
    """In between class that converts QT key events to Uranium events."""

    def __init__(self):
        super().__init__()

    def handleEvent(self, event):
        if event.type() == QEvent.Type.KeyPress:
            e = KeyEvent(KeyEvent.KeyPressEvent, self._qtKeyToUMKey(event.key()))
            self.event.emit(e)
        elif event.type() == QEvent.Type.KeyRelease:
            e = KeyEvent(KeyEvent.KeyReleaseEvent, self._qtKeyToUMKey(event.key()))
            self.event.emit(e)

    def _qtKeyToUMKey(self, key):
        if key == Qt.Key.Key_Shift:
            return KeyEvent.ShiftKey
        elif key == Qt.Key.Key_Control:
            return KeyEvent.ControlKey
        elif key == Qt.Key.Key_Alt:
            return KeyEvent.AltKey
        elif key == Qt.Key.Key_Space:
            return KeyEvent.SpaceKey
        elif key == Qt.Key.Key_Meta:
            return KeyEvent.MetaKey
        elif key == Qt.Key.Key_Enter or key == Qt.Key.Key_Return:
            return KeyEvent.EnterKey
        elif key == Qt.Key.Key_Up:
            return KeyEvent.UpKey
        elif key == Qt.Key.Key_Down:
            return KeyEvent.DownKey
        elif key == Qt.Key.Key_Left:
            return KeyEvent.LeftKey
        elif key == Qt.Key.Key_Right:
            return KeyEvent.RightKey
        elif key == Qt.Key.Key_Minus:
            return KeyEvent.MinusKey
        elif key == Qt.Key.Key_Underscore:
            return KeyEvent.UnderscoreKey
        elif key == Qt.Key.Key_Plus:
            return KeyEvent.PlusKey
        elif key == Qt.Key.Key_Equal:
            return KeyEvent.EqualKey

        return key
