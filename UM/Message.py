# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Signal import Signal

## Class for displaying messages in the application. 
#
class Message():
    def __init__(self, text = "", lifetime = 10, dismissable = True, progress = None):
        super().__init__()
        self._application = Application.getInstance()
        self._visible = False
        self._text = text
        self._progress = progress # If progress is set to -1, the progress is seen as indeterminate
        self._max_progress = 100
        self._lifetime = lifetime 
        self._lifetime_timer = None
        self._dismissable = dismissable # Can the message be closed by user?
        self._actions = []
    
    actionTriggered = Signal()
    
    ##  Show the message (if not already visible)
    def show(self):
        if not self._visible:
            self._visible = True
            self._application.showMessageSignal.emit(self)
    
    ##  Can the message be closed by user?
    def isDismissable(self):
        return self._dismissable
    
    ##  Set the lifetime timer of the message.
    #   This is used by the QT application once the message is shown.
    #   If the lifetime is set to 0, no timer is added.
    def setTimer(self, timer):
        self._lifetime_timer = timer
        if self._lifetime_timer:
            if self._lifetime:
                self._lifetime_timer.setInterval(self._lifetime * 1000)
                self._lifetime_timer.setSingleShot(True)
                self._lifetime_timer.timeout.connect(self.hide)
                self._lifetime_timer.start()

    def addAction(self, action_id, name, icon, description):
        self._actions.append({"action_id": action_id, "name": name, "icon": icon, "description": description})
    
    def getActions(self):
        return self._actions
    
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
        self.progressChanged.emit(self)

    progressChanged = Signal()

    def getProgress(self):
        return self._progress

    def hide(self):
        if self._visible:
            self._visible = False
            self._application.hideMessageSignal.emit(self)
