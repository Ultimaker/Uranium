# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from enum import IntEnum
import subprocess
import sys
import threading
from typing import Any, Dict, Optional, List, Callable, TextIO

from UM.Backend.GrpcBackendServer import GrpcBackendServer
from UM.Logger import Logger
from UM.Signal import Signal, signalemitter
import UM.Application
from UM.PluginObject import PluginObject
from UM.Platform import Platform

class BackendState(IntEnum):
    """
    The current processing state of the backend.

    :class:`BackendState` is an enumeration class that represents the different states that the backend can be in.

    Attributes:
        - NotStarted (int): The backend has not started processing.
        - Processing (int): The backend is currently processing data.
        - Done (int): The backend has finished processing successfully.
        - Error (int): The backend encountered an error during processing.
        - Disabled (int): The backend is disabled and cannot process data.
    """

    NotStarted = 1
    Processing = 2
    Done = 3
    Error = 4
    Disabled = 5


@signalemitter
class Backend(PluginObject):
    """
    Base class for any backend communication (separate piece of software).
    Cura supplies the Cura-specific gRPC service and protobuf message handlers.
    """

    def __init__(self) -> None:
        super().__init__()

        self._grpc_server: Optional[GrpcBackendServer] = None
        self._port = 49674
        self._process: Optional[subprocess.Popen] = None
        self._backend_log: List[bytes] = []
        self._backend_log_max_lines = None

        self._backend_state: BackendState = BackendState.NotStarted

        UM.Application.Application.getInstance().callLater(self._prepareBackendServer)

    processingProgress = Signal()
    backendStateChange = Signal()
    backendConnected = Signal()
    backendQuit = Signal()
    backendDone = Signal()

    def setState(self, new_state: BackendState) -> None:
        if new_state != self._backend_state:
            self._backend_state = new_state
            self.backendStateChange.emit(self._backend_state)

            if self._backend_state == BackendState.Done:
                self.backendDone.emit()

    def startEngine(self) -> None:
        """
        Start the backend / engine.
        Runs the engine, this is only called when the socket is fully opened & ready to accept connections
        """

        command = self.getEngineCommand()
        if not command:
            self._prepareBackendServer()
            return

        self._flushBackendLog()
        self._ensureOldProcessIsTerminated()

        self._process = self._runEngineProcess(command)
        if self._process is None:  # Failed to start engine.
            return
        Logger.log("i", "Started engine process: %s", self.getEngineCommand()[0])

        self._beginThreads()

    def _beginThreads(self) -> None:
        self._backendLog(bytes("Calling engine with: %s\n" % self.getEngineCommand(), "utf-8"))
        t = threading.Thread(target=self._storeOutputToLogThread, args=(self._process.stdout,),
                             name="EngineOutputThread")
        t.daemon = True
        t.start()
        t = threading.Thread(target=self._storeStderrToLogThread, args=(self._process.stderr,),
                             name="EngineErrorThread")
        t.daemon = True
        t.start()

    def _ensureOldProcessIsTerminated(self) -> None:
        if self._process is not None:
            try:
                self._process.terminate()
            except PermissionError:
                Logger.error("Unable to kill running engine. Access is denied.")
                return
            Logger.log("d", "Engine process is killed. Received return code %s", self._process.wait())

    def _flushBackendLog(self) -> None:
        if not self._backend_log_max_lines:
            self._backend_log = []

    def close(self) -> None:
        if self._grpc_server:
            self._grpc_server.stop()
            self._grpc_server = None

    @staticmethod
    def _decodeLine(line: bytes) -> str:
        try:
            return line.decode("utf-8")
        except UnicodeDecodeError:
            # We use Latin-1 as a fallback since it can never give decoding errors. All characters are 1 byte
            return line.decode("latin1")

    def _backendLog(self, line: bytes) -> None:
        line_str = self._decodeLine(line)
        Logger.log("d", "[Backend] " + line_str.strip())
        self._backend_log.append(line)

    def getLog(self) -> List[bytes]:
        """
        Returns the backend log.

        :return: A list of bytes representing the backend log.
        """
        if self._backend_log_max_lines and type(self._backend_log_max_lines) == int:
            while len(self._backend_log) >= self._backend_log_max_lines:
                del(self._backend_log[0])
        return self._backend_log

    def getEngineCommand(self) -> List[str]:
        """Get the command used to start the backend executable """

        return [UM.Application.Application.getInstance().getPreferences().getValue("backend/location"), "connect", f"127.0.0.1:{self._port}"]

    def _runEngineProcess(self, command_list: List[str]) -> Optional[subprocess.Popen]:
        """
        Start the (external) backend process.
        :param command_list:
        :return:
        """

        kwargs: Dict[str, Any] = {}
        if sys.platform == "win32":
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = su
        try:
            # STDIN needs to be None because we provide no input, but communicate via a local socket instead. The NUL device sometimes doesn't exist on some computers.
            # STDOUT and STDERR need to be pipes because we'd like to log the output on those channels into the application log.
            return subprocess.Popen(command_list, stdin = None, stdout = subprocess.PIPE, stderr = subprocess.PIPE, **kwargs)
        except PermissionError:
            Logger.log("e", "Couldn't start back-end: No permission to execute process.")
        except FileNotFoundError:
            Logger.logException("e", "Unable to find backend executable: %s", command_list[0])
        except BlockingIOError:
            Logger.log("e", "Couldn't start back-end: Resource is temporarily unavailable")
        except OSError as e:
            Logger.log("e", "Couldn't start back-end: Operating system is blocking it (antivirus?): {err}".format(err = str(e)))
        return None

    def _storeOutputToLogThread(self, handle):
        while True:
            try:
                line = handle.readline()
            except OSError:
                Logger.logException("w", "Exception handling stdout log from backend.")
                continue
            if line == b"":
                self.backendQuit.emit()
                break
            self._backendLog(line)

    def _storeStderrToLogThread(self, handle: TextIO) -> None:
        """
        Stores the standard error output from the backend process to the log.

        :param handle: The handle to the standard error output stream.
        :type handle: file-like object

        :return: None
        """
        while True:
            try:
                line = handle.readline()
            except OSError:
                Logger.logException("w", "Exception handling stderr log from backend.")
                continue
            if line == b"":
                break
            self._backendLog(line)

    def _prepareBackendServer(self) -> None:
        """Cura overrides this to install its generated Cura gRPC service."""
        raise NotImplementedError("Cura must install the Cura Engine gRPC service")

    def _createGrpcBackendServer(self, servicer, add_servicer) -> GrpcBackendServer:
        """Bind the localhost service endpoint and start its gRPC server."""
        if self._grpc_server:
            self._grpc_server.stop()
        self._grpc_server = GrpcBackendServer(servicer, add_servicer, first_port=self._port)
        self._grpc_server._on_stream_connected = self._onEngineConnected
        self._port = self._grpc_server.start()
        if UM.Application.Application.getInstance().getUseExternalBackend():
            Logger.log("i", "Listening for engine connections on %s", self._port)
        else:
            self.startEngine()
        return self._grpc_server

    def _onEngineConnected(self) -> None:
        Logger.log("d", "Engine connected on port %s", self._port)
        self.backendConnected.emit()
