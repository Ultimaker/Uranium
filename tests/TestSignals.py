# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
from unittest.mock import patch, MagicMock

import pytest

from UM import FlameProfiler
from UM.Signal import Signal, signalemitter, postponeSignals, CompressTechnique
from copy import deepcopy

class SignalReceiver:
    def __init__(self):
        self._emit_count = 0

    def getEmitCount(self):
        return self._emit_count

    def slot(self, *args, **kwargs):
        self._emit_count += 1


def test_signalWithFlameProfiler():
    with patch("UM.Signal._recordSignalNames", MagicMock(return_value = True)):
        FlameProfiler.record_profile = True
        test = SignalReceiver()

        signal = Signal(type=Signal.Direct)
        signal.connect(test.slot)
        signal.emit()

        assert test.getEmitCount() == 1
        FlameProfiler.record_profile = False


def test_doubleSignalWithFlameProfiler():
    FlameProfiler.record_profile = True
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal2 = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    signal2.connect(signal)
    signal2.emit()
    assert test.getEmitCount() == 1
    FlameProfiler.record_profile = False


def test_signal():
    test = SignalReceiver()

    signal = Signal(type = Signal.Direct)
    signal.connect(test.slot)
    signal.emit()

    assert test.getEmitCount() == 1

def test_postponeEmitNoCompression():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    with postponeSignals(signal, compress=CompressTechnique.NoCompression):
        signal.emit()
        assert test.getEmitCount() == 0  # as long as we're in this context, nothing should happen!
        signal.emit()
        assert test.getEmitCount() == 0
    assert test.getEmitCount() == 2


def test_postponeEmitCompressSingle():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    with postponeSignals(signal, compress=CompressTechnique.CompressSingle):
        signal.emit()
        assert test.getEmitCount() == 0  # as long as we're in this context, nothing should happen!
        signal.emit()
        assert test.getEmitCount() == 0
    assert test.getEmitCount() == 1

def test_postponeEmitCompressPerParameterValue():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    with postponeSignals(signal, compress=CompressTechnique.CompressPerParameterValue):
        signal.emit("ZOMG")
        assert test.getEmitCount() == 0  # as long as we're in this context, nothing should happen!
        signal.emit("ZOMG")
        assert test.getEmitCount() == 0
        signal.emit("BEEP")
    # We got 3 signal emits, but 2 of them were the same, so we end up with 2 unique emits.
    assert test.getEmitCount() == 2


def test_connectWhilePostponed():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    with postponeSignals(signal):
        signal.connect(test.slot)  # This won't do anything, as we're postponing at the moment!
        signal.emit()
    assert test.getEmitCount() == 0  # The connection was never made, so we should get 0


def test_disconnectWhilePostponed():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    with postponeSignals(signal):
        signal.disconnect(test.slot)  # This won't do anything, as we're postponing at the moment!
        signal.disconnectAll()  # Same holds true for the disconnect all
        signal.emit()
    assert test.getEmitCount() == 1  # Despite attempting to disconnect, this didn't happen because of the postpone


def test_disconnectAll():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    signal.disconnectAll()
    signal.emit()
    assert test.getEmitCount() == 0


def test_connectSelf():
    signal = Signal(type=Signal.Direct)
    signal.connect(signal)
    signal.emit()  # If they are connected, this crashes with a max recursion depth error


def test_deepCopy():
    test = SignalReceiver()

    signal = Signal(type=Signal.Direct)
    signal.connect(test.slot)
    copied_signal = deepcopy(signal)

    copied_signal.emit()
    # Even though the original signal was not called, the copied one should have the same result
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
