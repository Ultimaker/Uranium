from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot,pyqtSignal, pyqtProperty

class ToolbarProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._state = 1
        self._use_wizard = False
    
    stateChanged = pyqtSignal()
    wizardStateChanged = pyqtSignal()
    
    @pyqtProperty(bool,notify = wizardStateChanged)
    def wizardActive(self):
        return self._use_wizard
    
    @pyqtSlot(bool)
    def setWizardState(self, state):
        self._use_wizard = state
        self.wizardStateChanged.emit()
    
    @pyqtProperty(int,notify = stateChanged)
    def state(self):
        return self._state
    
    @pyqtSlot(int)
    def setState(self, state):
        self._state = state
        self.stateChanged.emit()