from concurrent.futures import ThreadPoolExecutor
from threading import Event
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
    server = GrpcBackendServer()
    envelope = object()

    assert server.send_message(envelope)
    assert server._outgoing.get_nowait() is envelope


def test_streamYieldsExitInstructionAndRemainsOpenUntilClientEnds():
    server = GrpcBackendServer()
    queued_output = MagicMock()
    exit_envelope = MagicMock()
    exit_envelope.WhichOneof.return_value = "exit_engine"

    context = MagicMock()
    context.is_active.return_value = True
    release_client = Event()
    request_received = Event()

    def requests():
        yield MagicMock()
        release_client.wait()

    server.messageReceived.emit = lambda _envelope: request_received.set()
    server.streamEnded.emit = MagicMock()
    responses = server.run_stream(requests(), context)
    end_of_stream = object()

    def next_response():
        try:
            return next(responses)
        except StopIteration:
            return end_of_stream

    with ThreadPoolExecutor(max_workers=1) as executor:
        response_future = executor.submit(next_response)
        try:
            assert request_received.wait(timeout=2)

            assert server.send_message(queued_output)
            assert response_future.result(timeout=2) is queued_output

            response_future = executor.submit(next_response)
            assert server.send_message(exit_envelope)
            assert response_future.result(timeout=2) is exit_envelope

            # ExitEngine is delivered to the engine, but the bidirectional stream stays
            # alive until the engine closes its request side.
            assert server.connected
            server.streamEnded.emit.assert_not_called()

            response_future = executor.submit(next_response)
            assert not response_future.done()
        finally:
            release_client.set()

        assert response_future.result(timeout=2) is end_of_stream

    assert not server.connected
    server.streamEnded.emit.assert_called_once_with(None)


def test_sendMessageReturnsFalseWhenQueueIsFull():
    server = GrpcBackendServer()

    for _ in range(server._outgoing.maxsize):
        assert server.send_message(object())

    assert not server.send_message(object())
