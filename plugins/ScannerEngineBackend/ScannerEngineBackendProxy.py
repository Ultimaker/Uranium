from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot,pyqtSignal, pyqtProperty,QUrl

from UM.Application import Application
import threading

class ScannerEngineBackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = Application.getInstance().getBackend()
        self._backend.newCameraImage.connect(self._onNewImage)
        self._backend.StatusMessage.connect(self._onStatusMessage)
        self._id = 0;
        self._backend.processingProgress.connect(self._onProcessingProgress)
        self._warning_string = ""
        self._resetStatusMessageTimer = None

    processingProgress = pyqtSignal(float, arguments = ['amount'])

    def _onProcessingProgress(self, amount):
        self.processingProgress.emit(amount)
    
    newImage = pyqtSignal()
    
    @pyqtProperty(QUrl, notify=newImage)
    def cameraImage(self):
        self._id += 1
        temp = "image://camera/" + str(self._id)
        return QUrl(temp,QUrl.TolerantMode)

    newStatusText = pyqtSignal()
    
    @pyqtProperty(str, notify=newStatusText)
    def warningText(self):
        return self._warning_string
    
    @pyqtSlot()
    def scan(self):
        self._backend.startScan()
    
    @pyqtSlot()
    def calibrate(self):
        self._backend.startCalibration()
    
    #Binding to convert our signal (newCameraImage from the backend) to pyQtSignal
    def _onNewImage(self):
        self.newImage.emit()
    
    def _onStatusMessage(self, str):
        self._warning_string = str
        if not self._resetStatusMessageTimer:
            self._resetStatusMessageTimer = threading.Timer(3, self._onResetStatsTimerFinished)
            self._resetStatusMessageTimer.start()
        if self._resetStatusMessageTimer: #Stop timer and create a new one.
            self._resetStatusMessageTimer.cancel()
            self._resetStatusMessageTimer = threading.Timer(3, self._onResetStatsTimerFinished) 
            self._resetStatusMessageTimer.start()
        self.newStatusText.emit()
    
    def _onResetStatsTimerFinished(self):
        self._warning_string = ""
        self._resetStatusMessageTimer = None
        self.newStatusText.emit()
    
    @pyqtSlot(int)
    def setCalibrationStep(self, step_number):
        self._backend.setCalibrationStep(step_number)
        pass
    
    #@pyqtSlot(str)    
    #def calibrationButtonPressed(self, key):
    #    self._backend.setCalibrationStep(key);