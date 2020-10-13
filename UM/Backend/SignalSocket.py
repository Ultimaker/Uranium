# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import Arcus

from UM.Signal import Signal, signalemitter


@signalemitter
class SignalSocket(Arcus.Socket):
    """A small extension of an Arcus socket that emits queued signals when socket events happen."""

    def __init__(self):
        super().__init__()

        self._listener = _SocketListener()
        self._listener.stateChangedCallback = self._onStateChanged
        self._listener.messageReceivedCallback = self._onMessageReceived
        self._listener.errorCallback = self._onError
        self.addListener(self._listener)

    stateChanged = Signal()
    messageReceived = Signal()
    error = Signal()

    def _onStateChanged(self, state):
        self.stateChanged.emit(state)

    def _onMessageReceived(self):
        self.messageReceived.emit()

    def _onError(self, error):
        self.error.emit(error)

class _SocketListener(Arcus.SocketListener):
    def __init__(self):
        super().__init__()

        self.stateChangedCallback = None
        self.messageReceivedCallback = None
        self.errorCallback = None

    def stateChanged(self, state):
        try:
            if self.stateChangedCallback:
                self.stateChangedCallback(state)
        except AttributeError:
            # For some reason, every so often, it seems to feel that the attribute stateChangedCallback doesn't exist.
            # Ignoring this prevents crashes.
            pass

    def messageReceived(self):
        if self.messageReceivedCallback:
            self.messageReceivedCallback()

    def error(self, error):
        if self.errorCallback:
            self.errorCallback(error)
