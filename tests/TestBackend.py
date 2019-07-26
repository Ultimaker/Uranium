from UM.Backend.Backend import Backend
import pytest
from unittest.mock import patch, MagicMock

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

