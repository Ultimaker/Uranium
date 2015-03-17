from PyQt5.QtCore import pyqtProperty, QObject, Qt, QCoreApplication
from PyQt5.QtGui import QColor
from PyQt5.QtQuick import QQuickWindow, QQuickItem

from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Qt.QtMouseDevice import QtMouseDevice
from UM.Qt.QtKeyDevice import QtKeyDevice
from UM.Application import Application

##  QQuickWindow subclass that provides the main window.
class MainWindow(QQuickWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        self._backgroundColor = QColor(204, 204, 204, 255)

        self.setClearBeforeRendering(False)
        self.beforeRendering.connect(self._render, type=Qt.DirectConnection)

        self._mouseDevice = QtMouseDevice(self)
        self._mouseDevice.setPluginId('qt_mouse')
        self._keyDevice = QtKeyDevice()
        self._keyDevice.setPluginId('qt_key')

        self._app = QCoreApplication.instance()
        self._app.getController().addInputDevice(self._mouseDevice)
        self._app.getController().addInputDevice(self._keyDevice)
        self._app.getController().getScene().sceneChanged.connect(self._onSceneChanged)

    def getBackgroundColor(self):
        return self._backgroundColor

    def setBackgroundColor(self, color):
        self._backgroundColor = color
        self._app.getRenderer().setBackgroundColor(color)

    backgroundColor = pyqtProperty(QColor, fget=getBackgroundColor, fset=setBackgroundColor)

#   Warning! Never reimplemented this as a QExposeEvent can cause a deadlock with QSGThreadedRender due to both trying
#   to claim the Python GIL.
#   def event(self, event):

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.isAccepted():
            return

        self._mouseDevice.handleEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.isAccepted():
            return

        self._mouseDevice.handleEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.isAccepted():
            return

        self._mouseDevice.handleEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.isAccepted():
            return

        self._keyDevice.handleEvent(event)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.isAccepted():
            return

        self._keyDevice.handleEvent(event)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if event.isAccepted():
            return

        self._mouseDevice.handleEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        w = event.size().width() / 2
        h = event.size().height() / 2
        for camera in self._app.getController().getScene().getAllCameras():
            camera.setViewportSize(w,h)
            proj = Matrix()
            if camera.isPerspective():
                proj.setPerspective(30, w/h, 1, 500)
            else:
                proj.setOrtho(-w, w, -h, h, -500, 500)
            camera.setProjectionMatrix(proj)

        self._app.getRenderer().setViewportSize(event.size().width(), event.size().height())

    def hideEvent(self, event):
        Application.getInstance().windowClosed()

    def _render(self):
        renderer = self._app.getRenderer()
        view = self._app.getController().getActiveView()

        renderer.beginRendering()
        view.beginRendering()
        renderer.renderQueuedNodes()
        view.endRendering()
        renderer.endRendering()

    def _onSceneChanged(self, object):
        self.update()
