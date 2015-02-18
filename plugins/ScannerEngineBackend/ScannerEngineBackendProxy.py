from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot,pyqtSignal, pyqtProperty,QUrl

from UM.Application import Application
import threading

class ScannerEngineBackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = Application.getInstance().getBackend()
        self._backend.newCameraImage.connect(self._onNewImage)
        self._backend.calibrationProblemMessage.connect(self._onCalibrationProblem)
        self._id = 0;
        self._backend.processingProgress.connect(self._onProcessingProgress)
        self._warning_string = ""
        self._resetProblemMessageTimer = None

    processingProgress = pyqtSignal(float, arguments = ['amount'])

    def _onProcessingProgress(self, amount):
        self.processingProgress.emit(amount)
    
    newImage = pyqtSignal()
    
    @pyqtProperty(QUrl, notify=newImage)
    def cameraImage(self):
        self._id += 1
        temp = "image://camera/" + str(self._id)
        return QUrl(temp,QUrl.TolerantMode)

    newCalibrationProblemText = pyqtSignal()
    
    @pyqtProperty(str, notify=newCalibrationProblemText)
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
    
    def _onCalibrationProblem(self, str):
        self._warning_string = str
        if not self._resetProblemMessageTimer:
            self._resetProblemMessageTimer = threading.Timer(3, self._onResetProblemTimerFinished)
            self._resetProblemMessageTimer.start()
        if self._resetProblemMessageTimer: #Stop timer and create a new one.
            self._resetProblemMessageTimer.cancel()
            self._resetProblemMessageTimer = threading.Timer(3, self._onResetProblemTimerFinished) 
            self._resetProblemMessageTimer.start()
        self.newCalibrationProblemText.emit()
    
    def _onResetProblemTimerFinished(self):
        self._warning_string = ""
        self._resetProblemMessageTimer = None
        self.newCalibrationProblemText.emit()
    
    @pyqtSlot(int)
    def setCalibrationStep(self, step_number):
        self._backend.setCalibrationStep(step_number)
        pass
    
    #@pyqtSlot(str)    
    #def calibrationButtonPressed(self, key):
    #    self._backend.setCalibrationStep(key);