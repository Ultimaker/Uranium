from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot,pyqtSignal, pyqtProperty

class ToolbarProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._state = 0
    
    stateChanged = pyqtSignal()
    
    @pyqtProperty(int,notify=stateChanged)
    def state(self):
        print("Caught statechanged")
        return self._state
    
    @pyqtSlot(int)
    def setState(self, state):
        self._state = state
        print("emitting stateChanged")
        self.stateChanged.emit()