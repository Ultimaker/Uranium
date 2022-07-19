# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

# The Window class inherits from QQuickWindow, making the use of Window roughly the same as QQuickWindow. As not all
# event handlers are exposed in the qml version of QQuickWindow we use python bindings to give us more control over the
# window object.

from PyQt6.QtCore import pyqtSlot
from PyQt6 import QtCore
from PyQt6.QtQuick import QQuickWindow


class Window(QQuickWindow):
    def __init__(self, parent=None) -> None:
        super(Window, self).__init__(parent=parent)
        self.update()

    def moveEvent(self, event):
        # When dragging a window between screens with different scaling settings we see some rendering artifacts. By
        # intercepting the window move event, and triggering an update on this move event we circumvent this issue.
        self.update()
        return super(Window, self).moveEvent(event)

    def showEvent(self, event):
        self.update()
        return super(Window, self).showEvent(event)

    def resizeEvent(self, event):
        self.update()
        return super(Window, self).resizeEvent(event)
