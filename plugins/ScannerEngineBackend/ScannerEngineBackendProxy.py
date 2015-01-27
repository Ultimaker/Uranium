from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot,pyqtSignal, pyqtProperty,QUrl

from UM.Application import Application

class ScannerEngineBackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = Application.getInstance().getBackend()
        self._backend.newCameraImage.connect(self._onNewImage)
        self._id = 0;
    
    newImage = pyqtSignal()
    
    @pyqtProperty(QUrl, notify=newImage)
    def cameraImage(self):
        self._id += 1
        temp = "image://camera/" + str(self._id)
        return QUrl(temp,QUrl.TolerantMode)
        
    @pyqtSlot()
    def scan(self):
        self._backend.startScan()
    
    @pyqtSlot()    
    def calibrate(self):
        self._backend.startCalibration()
    
    #Binding to convert our signal (newCameraImage from the backend) to pyQtSignal
    def _onNewImage(self):
        self.newImage.emit()