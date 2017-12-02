# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import pytest

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

def test_signalemitter():
    def declare_signalemitter():
        @signalemitter
        class Test:
            testSignal = Signal()

        return Test

    cls = declare_signalemitter()
    assert cls is not None

    inst = cls()
    assert cls is not None

    assert hasattr(inst, "testSignal")
    assert inst.testSignal != cls.testSignal

    def declare_bad_signalemitter():
        @signalemitter
        class Test:
            pass

        return Test

    with pytest.raises(TypeError):
        declare_bad_signalemitter()
