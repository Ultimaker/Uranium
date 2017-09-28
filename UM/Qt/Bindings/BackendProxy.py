# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty

from UM.i18n import i18nCatalog
from UM.Message import Message
from UM.Application import Application
from UM.Backend.Backend import BackendState

i18n_catalog = i18nCatalog("uranium")

class BackendProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._backend = Application.getInstance().getBackend()
        self._progress = -1
        self._state = BackendState.NotStarted
        if self._backend:
            self._backend.processingProgress.connect(self._onProcessingProgress)
            self._backend.backendStateChange.connect(self._onBackendStateChange)

    processingProgress = pyqtSignal(float, arguments = ["amount"])

    @pyqtProperty(float, notify = processingProgress)
    def progress(self):
        return self._progress

    backendStateChange = pyqtSignal(int, arguments = ["state"])

    ##  Returns the current state of processing of the backend.
    #
    #   \return \type{IntEnum} The current state of the backend.
    @pyqtProperty(int, notify = backendStateChange)
    def state(self):
        return self._state

    def _onProcessingProgress(self, amount):
        self._progress = amount
        self.processingProgress.emit(amount)

    def _onBackendStateChange(self, state):
        self._state = state
        self.backendStateChange.emit(state)