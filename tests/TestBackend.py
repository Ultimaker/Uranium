import sys
from unittest.mock import patch, MagicMock

import pytest

import Arcus

from UM.Backend.Backend import Backend

@pytest.fixture
def backend():
    with patch("UM.Application.Application.getInstance"):
        backend = Backend()
        return backend

@pytest.fixture
def process():
    mocked_process = MagicMock()
    mocked_process.stderr.readline = MagicMock()
    mocked_process.stderr.readline.side_effect= [b"blarg", b"", b""]

    mocked_process.stdout.readline = MagicMock()
    mocked_process.stdout.readline.side_effect = [b"blarg", b"", b""]
    return mocked_process


def test_setState(backend):
    backend.backendStateChange.emit = MagicMock()

    backend.setState("BEEP")
    backend.backendStateChange.emit.assert_called_once_with("BEEP")

    # Calling it again should not cause another emit
    backend.setState("BEEP")
    backend.backendStateChange.emit.assert_called_once_with("BEEP")


def test_startEngine(backend, process):
    backend.getEngineCommand = MagicMock(return_value = "blarg")

    backend._runEngineProcess = MagicMock(return_value = process)

    backend.startEngine()
    backend._runEngineProcess.assert_called_once_with("blarg")

    backend.startEngine()
    process.terminate.assert_called_once_with()


def test_startEngineWithoutCommand(backend):
    backend.getEngineCommand = MagicMock(return_value = None)

    backend._createSocket = MagicMock()

    backend.startEngine()
    backend._createSocket.assert_called_once_with()


def test__onSocketStateChanged_listening(backend):
    backend.startEngine = MagicMock()
    with patch("UM.Application.Application.getInstance"):
        backend._onSocketStateChanged(Arcus.SocketState.Listening)
    assert backend.startEngine.called_once_with()


def test_onSocketStateChanged_connected(backend):
    backend.backendConnected = MagicMock()
    backend._onSocketStateChanged(Arcus.SocketState.Connected)
    assert backend.backendConnected.emit.called_once_with()


def test_handleKnownMessage(backend):
    handler = MagicMock()
    backend._message_handlers = {"beep": handler}
    socket = MagicMock()
    message = MagicMock()
    message.getTypeName = MagicMock(return_value = "beep")
    socket.takeNextMessage = MagicMock(return_value = message)
    backend._socket = socket
    backend._onMessageReceived()

    handler.assert_called_once_with(message)


def test_onSocketBindFailed(backend):
    port = backend._port
    backend._createSocket = MagicMock()
    bind_failed_error = MagicMock()
    bind_failed_error.getErrorCode = MagicMock(return_value=Arcus.ErrorCode.BindFailedError)
    backend._onSocketError(bind_failed_error)
    assert backend._createSocket.call_count == 1
    assert port + 1 == backend._port


def test_getLog(backend):
    backend._backendLog(b"blooop")

    assert backend.getLog() == [b"blooop"]

    backend._backend_log_max_lines = 3

    backend._backendLog(b"omgzomg")
    backend._backendLog(b"omgzomg2")
    # The max lines keeps deleting until the number of entries left is lower than the max (2 in this case)
    assert backend.getLog() == [b"omgzomg", b"omgzomg2"]


@pytest.mark.parametrize("exception", [PermissionError, FileNotFoundError, BlockingIOError])
def test_runEngineProcessException(backend, exception):
    # It should be able to handle a number of exceptions without problems
    with patch('subprocess.Popen', side_effect = exception):
        assert backend._runEngineProcess([""]) is None


def test_createSocket(backend):
    # We're not testing the signal socket here, so mock it
    mocked_signal_socket = MagicMock()
    with patch("UM.Backend.Backend.SignalSocket", MagicMock(return_value = mocked_signal_socket)):
        with patch("UM.Application.Application.getInstance"):
            backend._createSocket("beep")

            if sys.platform == "win32":
                mocked_signal_socket.registerAllMessageTypes.assert_called_once_with(b"beep")
            else:
                mocked_signal_socket.registerAllMessageTypes.assert_called_once_with("beep")

            # Try to create it again.
            backend._createSocket("beep")
            mocked_signal_socket.close.assert_called_once_with()

            backend.close()
            assert mocked_signal_socket.close.call_count == 2