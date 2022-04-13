# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty

from UM.i18n import i18nCatalog
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

    @pyqtProperty(int, constant = True)
    def NotStarted(self):
        return 1

    @pyqtProperty(int, constant=True)
    def Processing(self):
        return 2

    @pyqtProperty(int, constant=True)
    def Done(self):
        return 3

    @pyqtProperty(int, constant=True)
    def Error(self):
        return 4

    @pyqtProperty(int, constant=True)
    def Disabled(self):
        return 5

    backendStateChange = pyqtSignal(int, arguments = ["state"])

    @pyqtProperty(int, notify = backendStateChange)
    def state(self):
        """Returns the current state of processing of the backend.

        :return: :type{IntEnum} The current state of the backend.
        """

        return self._state

    def _onProcessingProgress(self, amount):
        if self._progress != amount:
            self._progress = amount
            self.processingProgress.emit(amount)

    def _onBackendStateChange(self, state):
        if self._state != state:
            self._state = state
            self.backendStateChange.emit(state)
