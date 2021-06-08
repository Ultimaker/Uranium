# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import pyqtProperty, Qt, QCoreApplication, pyqtSignal, pyqtSlot, QMetaObject, QRectF, QRect
from PyQt5.QtGui import QColor
from PyQt5.QtQuick import QQuickWindow

from UM.Logger import Logger
from UM.Math.Matrix import Matrix
from UM.Qt.QtMouseDevice import QtMouseDevice
from UM.Qt.QtKeyDevice import QtKeyDevice
from UM.Application import Application
from UM.Scene.Selection import Selection
from UM.Signal import Signal, signalemitter
from UM.Scene.Camera import Camera
from typing import Optional


@signalemitter
class MainWindow(QQuickWindow):
    """QQuickWindow subclass that provides the main window."""
    DEFAULT_WINDOW_WIDTH = 1280
    DEFAULT_WINDOW_HEIGHT = 720
    DEFAULT_WINDOW_LEFT = 50
    DEFAULT_WINDOW_TOP = 50


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
        self._app.getController().activeViewChanged.connect(self._onActiveViewChanged)
        Selection.selectionChanged.connect(self._onSceneChanged)
        self._preferences = Application.getInstance().getPreferences()

        self._preferences.addPreference("general/window_width", self.DEFAULT_WINDOW_WIDTH)
        self._preferences.addPreference("general/window_height", self.DEFAULT_WINDOW_HEIGHT)
        self._preferences.addPreference("general/window_left", self.DEFAULT_WINDOW_LEFT)
        self._preferences.addPreference("general/window_top", self.DEFAULT_WINDOW_TOP)
        self._preferences.addPreference("general/window_state", Qt.WindowNoState)
        self._preferences.addPreference("general/restore_window_geometry", True)

        restored_geometry = QRect(int(self._preferences.getValue("general/window_left")),
                                  int(self._preferences.getValue("general/window_top")),
                                  int(self._preferences.getValue("general/window_width")),
                                  int(self._preferences.getValue("general/window_height")))

        if not self._preferences.getValue("general/restore_window_geometry"):
            # Ignore whatever the preferences said.
            Logger.log("i", "Not restoring window geometry from preferences because 'restore_window_geometry' is false")
            restored_geometry = QRect(self.DEFAULT_WINDOW_LEFT,
                                      self.DEFAULT_WINDOW_TOP,
                                      self.DEFAULT_WINDOW_WIDTH,
                                      self.DEFAULT_WINDOW_HEIGHT)

        # Make sure restored geometry is not outside the currently available screens
        screen_found = False
        for s in range(0, self._app.desktop().screenCount()):
            if restored_geometry.intersects(self._app.desktop().availableGeometry(s)):
                screen_found = True
                break

        if not screen_found:
            Logger.log("w", "Could not restore to previous location on screen, since the sizes or number of monitors "
                            "have changed since then")
            # Unable to find the screen that this window used to be on, so just use the defaults
            restored_geometry = QRect(self.DEFAULT_WINDOW_LEFT,
                                      self.DEFAULT_WINDOW_TOP,
                                      self.DEFAULT_WINDOW_WIDTH,
                                      self.DEFAULT_WINDOW_HEIGHT)

        self.setGeometry(restored_geometry)
        self.setWindowState(int(self._preferences.getValue("general/window_state")))

        self._mouse_x = 0
        self._mouse_y = 0

        self._mouse_pressed = False

        self._viewport_rect = QRectF(0, 0, 1.0, 1.0)

        self.closing.connect(self.preClosing)

        Application.getInstance().setMainWindow(self)
        self._fullscreen = False

        self._full_render_required = True

        self._allow_resize = True

    # This event is triggered before hideEvent(self, event) event and might prevent window closing if
    # does not pass the check, for example if USB printer is printing
    # The implementation is in Cura.qml
    preClosing = pyqtSignal("QQuickCloseEvent*", arguments = ["close"])

    def setAllowResize(self, allow_resize: bool):
        if self._allow_resize != allow_resize:
            if not allow_resize:
                self.setMaximumHeight(self.height())
                self.setMinimumHeight(self.height())
                self.setMaximumWidth(self.width())
                self.setMinimumWidth(self.width())
            else:
                self.setMaximumHeight(16777215)
                self.setMinimumHeight(0)
                self.setMaximumWidth(16777215)
                self.setMinimumWidth(0)
            self._allow_resize = allow_resize

    @pyqtSlot()
    def toggleFullscreen(self):
        if self._fullscreen:
            self.setVisibility(QQuickWindow.Windowed)  # Switch back to windowed
        else:
            self.setVisibility(QQuickWindow.FullScreen)  # Go to fullscreen
        self._fullscreen = not self._fullscreen

    @pyqtSlot()
    def exitFullscreen(self):
        self.setVisibility(QQuickWindow.Windowed)
        self._fullscreen = False

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

        if self._mouse_pressed:
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
        if self._full_render_required:
            renderer = self._app.getRenderer()
            view = self._app.getController().getActiveView()
            renderer.beginRendering()
            view.beginRendering()
            renderer.render()
            view.endRendering()
            renderer.endRendering()
            self._full_render_required = False
            self.renderCompleted.emit()
        else:
            self._app.getRenderer().reRenderLast()

    def _onSceneChanged(self, object = None):
        self._full_render_required = True
        self.update()

    def _onActiveViewChanged(self):
        self._full_render_required = True
        self.update()

    @pyqtSlot()
    def _onWindowGeometryChanged(self):
        # Do not store maximised window geometry, but store state instead
        # Using windowState instead of isMaximized is a workaround for QTBUG-30085
        if self.windowState() == Qt.WindowNoState:
            self._preferences.setValue("general/window_width", self.width())
            self._preferences.setValue("general/window_height", self.height())
            self._preferences.setValue("general/window_left", self.x())
            self._preferences.setValue("general/window_top", self.y())

        if self.windowState() in (Qt.WindowNoState, Qt.WindowMaximized):
            self._preferences.setValue("general/window_state", self.windowState())

    def _updateViewportGeometry(self, width: int, height: int) -> None:
        view_width = round(width * self._viewport_rect.width())
        view_height = round(height * self._viewport_rect.height())

        for camera in self._app.getController().getScene().getAllCameras():
            camera.setWindowSize(width, height)

            if camera.getAutoAdjustViewPort():
                camera.setViewportSize(view_width, view_height)

        self._app.getRenderer().setViewportSize(view_width, view_height)
        self._app.getRenderer().setWindowSize(width, height)
