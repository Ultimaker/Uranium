from UM.Application import Application
from PyQt5.QtCore import QTimer

## Class for displaying messages in the application. 
class Message():
    def __init__(self, text = "", lifetime = 10):
        super().__init__()
        self._application = Application.getInstance()
        self._visible = False
        self._text = text
        self._progress = 0
        self._max_progress = 0
        self._lifetime = lifetime #TODO: add kill timer (qtimer)
        self._lifetime_timer = QTimer()
        self._lifetime_timer.setInterval(lifetime * 1000)
        self._lifetime_timer.setSingleShot(True)
        self._lifetime_timer.timeout.connect(self.hide)
    
    def show(self):
        if not self._visible:
            self._lifetime_timer.start()
            self._visible = True
            self._application.showMessage(self)
            
    def setText(self, text):
        self._text = text
        
    def getText(self):
        return self._text
    
    def setMaxProgress(self, max_progress):
        self._max_progress = max_progress
    
    def getMaxProgress(self):
        return self._max_progress
    
    def setProgress(self, progress):
        self._progress = progress
        
    def getProgress(self):
        return self._progress
    
    def hide(self):
        if self._visible:
            self._lifetime_timer.stop()
            self._visible = False
            self._application.hideMessage(self)