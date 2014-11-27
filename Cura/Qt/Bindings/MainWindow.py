from PyQt5.QtCore import pyqtProperty, QObject, Qt, QCoreApplication
from PyQt5.QtGui import QColor
from PyQt5.QtQuick import QQuickWindow, QQuickItem

from OpenGL import GL
from OpenGL.GL.GREMEDY.string_marker import *

from Cura.Math.Vector import Vector
from Cura.Qt.QtMouseDevice import QtMouseDevice
from Cura.Qt.QtKeyDevice import QtKeyDevice

##  QQuickWindow subclass that provides the main window.
class MainWindow(QQuickWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        self._backgroundColor = QColor(204, 204, 204, 255)

        self.setClearBeforeRendering(False)
        self.beforeRendering.connect(self._render, type=Qt.DirectConnection)

        self._mouseDevice = QtMouseDevice()
        self._keyDevice = QtKeyDevice()

        self._app = QCoreApplication.instance()
        self._app.getController().addInputDevice("Mouse", self._mouseDevice)
        self._app.getController().addInputDevice("Keyboard", self._keyDevice)
        self._app.getController().getScene().sceneChanged.connect(self._onSceneChanged)

    #def getApplication(self):
        #return self._app

    #def setApplication(self, app):
        #if app == self._app:
            #return

        #if self._app:
            #self._app.getController().removeInputDevice("Mouse")
            #self._app.getController().removeInputDevice("Keyboard")
            #self._app.getController().getScene().sceneChanged.disconnect(self.update)

        #self._app = app
        #if self._app:


    #application = pyqtProperty(QObject, fget=getApplication, fset=setApplication)

    def getBackgroundColor(self):
        return self._backgroundColor

    def setBackgroundColor(self, color):
        self._backgroundColor = color

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

    def _render(self):
        if bool(glStringMarkerGREMEDY):
            msg = b"Begin Rendering Background"
            glStringMarkerGREMEDY(len(msg), msg)

        GL.glClearColor(self._backgroundColor.redF(), self._backgroundColor.greenF(), self._backgroundColor.blueF(), self._backgroundColor.alphaF())
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self._app.getController().getActiveView().render()

        if bool(glStringMarkerGREMEDY):
            msg = "End Rendering Background"
            glStringMarkerGREMEDY(len(msg), msg)

    def _onSceneChanged(self, object):
        self.update()
