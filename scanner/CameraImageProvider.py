from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets
from UM.Application import Application
''' class CameraImageProvider(QtQuick.QQuickImageProvider):
    def __init__(self):
        QtQuick.QQuickImageProvider.__init__(self, QtQuick.QQuickImageProvider.Image)''' 
        
class CameraImageProvider(QtQuick.QQuickImageProvider):
    def __init__(self):
        
        QtQuick.QQuickImageProvider.__init__(self, QtQuick.QQuickImageProvider.Image)
        self._image = QtGui.QImage(250,250,QtGui.QImage.Format_RGB888)
        self._backend = Application.getInstance().getBackend()
    
    def setImage(self,image):
        self._image = image
    
    def requestImage(self, id, size):
        return self._backend.getLatestCameraImage(),QtCore.QSize(250, 250)
