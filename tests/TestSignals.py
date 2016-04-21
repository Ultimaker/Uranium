# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Signal import Signal, signalemitter

class SignalReceiver:
    def __init__(self):
        self._emit_count = 0

    def getEmitCount(self):
        return self._emit_count

    def slot(self):
        self._emit_count += 1

def test_signal():
    test = SignalReceiver()

    signal = Signal(type = Signal.Direct)
    signal.connect(test.slot)
    signal.emit()

    assert test.getEmitCount() == 1
