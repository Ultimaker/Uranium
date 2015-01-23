import Arcus

from UM.Signal import Signal, SignalEmitter

##  A small extension of an Arcus socket that emits queued signals when socket events happen.
class SignalSocket(Arcus.Socket, SignalEmitter):
    def __init__(self):
        super().__init__()

        self.setStateChangedCallback(self._onStateChanged)
        self.setMessageReceivedCallback(self._onMessageReceived)
        self.setErrorCallback(self._onError)

    stateChanged = Signal(type = Signal.Queued)

    messageReceived = Signal(type = Signal.Queued)

    error = Signal(type = Signal.Queued)

    def _onStateChanged(self, state):
        self.stateChanged.emit(state)

    def _onMessageReceived(self):
        self.messageReceived.emit()

    def _onError(self, error):
        self.error.emit(error)

