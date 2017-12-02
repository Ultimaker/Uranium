# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Qt.Factory.QtCore import pyqtProperty, Qt, QCoreApplication, pyqtSignal, pyqtSlot, QMetaObject, QRectF
from UM.Qt.Factory.QtGui import QColor
from UM.Qt.Factory.QtQuick import QQuickWindow

from UM.Math.Matrix import Matrix
from UM.Qt.QtMouseDevice import QtMouseDevice
from UM.Qt.QtKeyDevice import QtKeyDevice
from UM.Application import Application
from UM.Preferences import Preferences
from UM.Signal import Signal, signalemitter

from typing import Optional

MYPY = False
if MYPY:
    from UM.Qt.Factory.QtQuick import QQuickItem

##  QQuickWindow subclass that provides the main window.
@signalemitter
class MainWindow(QQuickWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        self._background_color = QColor(204, 204, 204, 255)

        self.setClearBeforeRendering(False)
        self.beforeRendering.connect(self._render, type = Qt.DirectConnection)

        self._mouse_device = QtMouseDevice(self)
        self._mouse_device.setPluginId("qt_mouse")
        self._key_device = QtKeyDevice()
        self._key_device.setPluginId("qt_key")
        self._previous_focus = None  # type: Optional["QQuickItem"]

        self._app = QCoreApplication.instance()

        # Remove previously added input devices (if any). This can happen if the window was re-loaded.
        self._app.getController().removeInputDevice("qt_mouse")
        self._app.getController().removeInputDevice("qt_key")

        self._app.getController().addInputDevice(self._mouse_device)
        self._app.getController().addInputDevice(self._key_device)
        self._app.getController().getScene().sceneChanged.connect(self._onSceneChanged)
        self._preferences = Preferences.getInstance()

        self._preferences.addPreference("general/window_width", 1280)
        self._preferences.addPreference("general/window_height", 720)
        self._preferences.addPreference("general/window_left", 50)
        self._preferences.addPreference("general/window_top", 50)
        self._preferences.addPreference("general/window_state", Qt.WindowNoState)

        # Restore window geometry
        self.setWidth(int(self._preferences.getValue("general/window_width")))
        self.setHeight(int(self._preferences.getValue("general/window_height")))
        self.setPosition(int(self._preferences.getValue("general/window_left")), int(self._preferences.getValue("general/window_top")))

        # Make sure restored geometry is not outside the currently available screens
        screen_found = False
        for s in range(0, self._app.desktop().screenCount()):
            if self.geometry().intersects(self._app.desktop().availableGeometry(s)):
                screen_found = True
                break
        if not screen_found:
            self.setPosition(50, 50)

        self.setWindowState(int(self._preferences.getValue("general/window_state")))
        self._mouse_x = 0
        self._mouse_y = 0

        self._mouse_pressed = False

        self._viewport_rect = QRectF(0, 0, 1.0, 1.0)

        Application.getInstance().setMainWindow(self)
        self._fullscreen = False

    @pyqtSlot()
    def toggleFullscreen(self):
        if self._fullscreen:
            self.setVisibility(QQuickWindow.Windowed)  # Switch back to windowed
        else:
            self.setVisibility(QQuickWindow.FullScreen)  # Go to fullscreen
        self._fullscreen = not self._fullscreen

    def getBackgroundColor(self):
        return self._background_color

    def setBackgroundColor(self, color):
        self._background_color = color
        self._app.getRenderer().setBackgroundColor(color)

    backgroundColor = pyqtProperty(QColor, fget=getBackgroundColor, fset=setBackgroundColor)

    mousePositionChanged = pyqtSignal()

    @pyqtProperty(int, notify = mousePositionChanged)
    def mouseX(self):
        return self._mouse_x

    @pyqtProperty(int, notify = mousePositionChanged)
    def mouseY(self):
        return self._mouse_y

    def setViewportRect(self, rect):
        if rect != self._viewport_rect:
            self._viewport_rect = rect
            self._updateViewportGeometry(self.width() * self.devicePixelRatio(), self.height() * self.devicePixelRatio())
            self.viewportRectChanged.emit()

    viewportRectChanged = pyqtSignal()

    @pyqtProperty(QRectF, fset = setViewportRect, notify = viewportRectChanged)
    def viewportRect(self):
        return self._viewport_rect

#   Warning! Never reimplemented this as a QExposeEvent can cause a deadlock with QSGThreadedRender due to both trying
#   to claim the Python GIL.
#   def event(self, event):

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.isAccepted():
            return

        if self.activeFocusItem() is not None and self.activeFocusItem() != self._previous_focus:
            self.activeFocusItem().setFocus(False)

        self._previous_focus = self.activeFocusItem()
        self._mouse_device.handleEvent(event)
        self._mouse_pressed = True

    def mouseMoveEvent(self, event):
        self._mouse_x = event.x()
        self._mouse_y = event.y()

        if self._mouse_pressed and self._app.getController().isModelRenderingEnabled():
            self.mousePositionChanged.emit()

        super().mouseMoveEvent(event)
        if event.isAccepted():
            return

        self._mouse_device.handleEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.isAccepted():
            return
        self._mouse_device.handleEvent(event)
        self._mouse_pressed = False

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.isAccepted():
            return

        self._key_device.handleEvent(event)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.isAccepted():
            return

        self._key_device.handleEvent(event)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if event.isAccepted():
            return

        self._mouse_device.handleEvent(event)

    def moveEvent(self, event):
        QMetaObject.invokeMethod(self, "_onWindowGeometryChanged", Qt.QueuedConnection)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        win_w = event.size().width() * self.devicePixelRatio()
        win_h = event.size().height() * self.devicePixelRatio()

        self._updateViewportGeometry(win_w, win_h)

        QMetaObject.invokeMethod(self, "_onWindowGeometryChanged", Qt.QueuedConnection)

    def hideEvent(self, event):
        if Application.getInstance().getMainWindow() == self:
            Application.getInstance().windowClosed()

    renderCompleted = Signal(type = Signal.Queued)

    def _render(self):
        renderer = self._app.getRenderer()
        view = self._app.getController().getActiveView()

        renderer.beginRendering()
        view.beginRendering()
        renderer.render()
        view.endRendering()
        renderer.endRendering()
        self.renderCompleted.emit()

    def _onSceneChanged(self, object):
        self.update()

    @pyqtSlot()
    def _onWindowGeometryChanged(self):
        if self.windowState() == Qt.WindowNoState:
            self._preferences.setValue("general/window_width", self.width())
            self._preferences.setValue("general/window_height", self.height())
            self._preferences.setValue("general/window_left", self.x())
            self._preferences.setValue("general/window_top", self.y())
            self._preferences.setValue("general/window_state", Qt.WindowNoState)
        elif self.windowState() == Qt.WindowMaximized:
            self._preferences.setValue("general/window_state", Qt.WindowMaximized)

    def _updateViewportGeometry(self, width: int, height: int):
        view_width = width * self._viewport_rect.width()
        view_height = height * self._viewport_rect.height()

        for camera in self._app.getController().getScene().getAllCameras():
            camera.setWindowSize(width, height)

            if camera.getAutoAdjustViewPort():
                camera.setViewportSize(view_width, view_height)
                projection_matrix = Matrix()
                if camera.isPerspective():
                    if view_width is not 0:
                        projection_matrix.setPerspective(30, view_width / view_height, 1, 500)
                else:
                    projection_matrix.setOrtho(-view_width / 2, view_width / 2, -view_height / 2, view_height / 2, -500, 500)
                camera.setProjectionMatrix(projection_matrix)

        self._app.getRenderer().setViewportSize(view_width, view_height)
        self._app.getRenderer().setWindowSize(width, height)
