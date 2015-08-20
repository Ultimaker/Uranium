# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import Arcus

from UM.Signal import Signal, SignalEmitter

##  A small extension of an Arcus socket that emits queued signals when socket events happen.
class SignalSocket(SignalEmitter, Arcus.Socket):
    def __init__(self):
        super().__init__()

        self.setStateChangedCallback(self._onStateChanged)
        self.setMessageReceivedCallback(self._onMessageReceived)
        self.setErrorCallback(self._onError)

    stateChanged = Signal()

    messageReceived = Signal()

    error = Signal()

    def _onStateChanged(self, state):
        self.stateChanged.emit(state)

    def _onMessageReceived(self):
        self.messageReceived.emit()

    def _onError(self, error):
        self.error.emit(error)

