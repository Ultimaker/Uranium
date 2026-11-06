from unittest.mock import patch, MagicMock

import pytest

from UM.Backend.Backend import Backend
from UM.Backend.GrpcBackendServer import GrpcBackendServer

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

    backend._prepareBackendServer = MagicMock()

    backend.startEngine()
    backend._prepareBackendServer.assert_called_once_with()


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


def test_closeStopsGrpcServer(backend):
    server = MagicMock()
    backend._grpc_server = server
    backend.close()
    server.stop.assert_called_once_with()
    assert backend._grpc_server is None


def test_sendMessageQueuesBeforeEngineConnection():
    with patch("UM.Backend.GrpcBackendServer.Application.getInstance") as application:
        application.return_value.callLater = MagicMock()
        server = GrpcBackendServer(MagicMock(), MagicMock())
    envelope = object()

    assert server.send_message(envelope)
    assert server._outgoing.get_nowait() is envelope


def test_exitInstructionClosesStreamAfterQueuedMessages():
    with patch("UM.Backend.GrpcBackendServer.Application.getInstance") as application:
        application.return_value.callLater = MagicMock()
        server = GrpcBackendServer(MagicMock(), MagicMock())
    queued_output = MagicMock()
    exit_envelope = MagicMock()
    exit_envelope.WhichOneof.return_value = "exit_engine"
    assert server.send_message(queued_output)
    assert server.send_message(exit_envelope)

    context = MagicMock()
    context.is_active.return_value = True
    with patch("UM.Backend.GrpcBackendServer.threading.Thread") as thread:
        responses = server.run_stream(iter(()), context, MagicMock())
        assert next(responses) is queued_output
        assert next(responses) is exit_envelope
        with pytest.raises(StopIteration):
            next(responses)
        thread.return_value.start.assert_called_once_with()
