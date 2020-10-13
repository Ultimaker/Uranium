# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from enum import IntEnum
import struct
import subprocess
import sys
import threading
from time import sleep
from typing import Any, Dict, Optional

from UM.Backend.SignalSocket import SignalSocket
from UM.Logger import Logger
from UM.Signal import Signal, signalemitter
import UM.Application
from UM.PluginObject import PluginObject
from UM.Platform import Platform

import Arcus


class BackendState(IntEnum):
    """The current processing state of the backend."""

    NotStarted = 1
    Processing = 2
    Done = 3
    Error = 4
    Disabled = 5


@signalemitter
class Backend(PluginObject):
    """Base class for any backend communication (separate piece of software).
    It makes use of the Socket class from libArcus for the actual communication bits.
    The message_handlers dict should be filled with string (full name of proto message), function pairs.
    """

    def __init__(self):
        super().__init__()  # Call super to make multiple inheritance work.
        self._supported_commands = {}

        self._message_handlers = {}

        self._socket = None
        self._port = 49674
        self._process = None # type: Optional[subprocess.Popen]
        self._backend_log = []
        self._backend_log_max_lines = None

        self._backend_state = BackendState.NotStarted

        UM.Application.Application.getInstance().callLater(self._createSocket)

    processingProgress = Signal()
    backendStateChange = Signal()
    backendConnected = Signal()
    backendQuit = Signal()

    def setState(self, new_state):
        if new_state != self._backend_state:
            self._backend_state = new_state
            self.backendStateChange.emit(self._backend_state)

    def startEngine(self):
        """:brief Start the backend / engine.
        Runs the engine, this is only called when the socket is fully opened & ready to accept connections
        """

        command = self.getEngineCommand()
        if not command:
            self._createSocket()
            return

        if not self._backend_log_max_lines:
            self._backend_log = []

        # Double check that the old process is indeed killed.
        if self._process is not None:
            try:
                self._process.terminate()
            except PermissionError:
                Logger.log("e", "Unable to kill running engine. Access is denied.")
                return
            Logger.log("d", "Engine process is killed. Received return code %s", self._process.wait())

        self._process = self._runEngineProcess(command)
        if self._process is None:  # Failed to start engine.
            return
        Logger.log("i", "Started engine process: %s", self.getEngineCommand()[0])
        self._backendLog(bytes("Calling engine with: %s\n" % self.getEngineCommand(), "utf-8"))
        t = threading.Thread(target = self._storeOutputToLogThread, args = (self._process.stdout,), name = "EngineOutputThread")
        t.daemon = True
        t.start()
        t = threading.Thread(target = self._storeStderrToLogThread, args = (self._process.stderr,), name = "EngineErrorThread")
        t.daemon = True
        t.start()

    def close(self):
        if self._socket:
            while self._socket.getState() == Arcus.SocketState.Opening:
                sleep(0.1)
            self._socket.close()

    def _backendLog(self, line):
        try:
            line_str = line.decode("utf-8")
        except UnicodeDecodeError:
            line_str = line.decode("latin1") #Latin-1 as a fallback since it can never give decoding errors. All characters are 1 byte.
        Logger.log("d", "[Backend] " + line_str.strip())
        self._backend_log.append(line)

    def getLog(self):
        """Get the logging messages of the backend connection."""

        if self._backend_log_max_lines and type(self._backend_log_max_lines) == int:
            while len(self._backend_log) >= self._backend_log_max_lines:
                del(self._backend_log[0])
        return self._backend_log

    def getEngineCommand(self):
        """Get the command used to start the backend executable """

        return [UM.Application.Application.getInstance().getPreferences().getValue("backend/location"), "--port", str(self._socket.getPort())]

    def _runEngineProcess(self, command_list) -> Optional[subprocess.Popen]:
        """Start the (external) backend process."""

        kwargs = {} #type: Dict[str, Any]
        if sys.platform == "win32":
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = su
            kwargs["creationflags"] = 0x00004000  # BELOW_NORMAL_PRIORITY_CLASS
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

    def _storeStderrToLogThread(self, handle):
        while True:
            try:
                line = handle.readline()
            except OSError:
                Logger.logException("w", "Exception handling stderr log from backend.")
                continue
            if line == b"":
                break
            self._backendLog(line)

    def _onSocketStateChanged(self, state):
        """Private socket state changed handler."""

        self._logSocketState(state)
        if state == Arcus.SocketState.Listening:
            if not UM.Application.Application.getInstance().getUseExternalBackend():
                self.startEngine()
        elif state == Arcus.SocketState.Connected:
            Logger.log("d", "Backend connected on port %s", self._port)
            self.backendConnected.emit()

    def _logSocketState(self, state):
        """Debug function created to provide more info for CURA-2127"""

        if state == Arcus.SocketState.Listening:
            Logger.log("d", "Socket state changed to Listening")
        elif state == Arcus.SocketState.Connecting:
            Logger.log("d", "Socket state changed to Connecting")
        elif state == Arcus.SocketState.Connected:
            Logger.log("d", "Socket state changed to Connected")
        elif state == Arcus.SocketState.Error:
            Logger.log("d", "Socket state changed to Error")
        elif state == Arcus.SocketState.Closing:
            Logger.log("d", "Socket state changed to Closing")
        elif state == Arcus.SocketState.Closed:
            Logger.log("d", "Socket state changed to Closed")

    def _onMessageReceived(self):
        """Private message handler"""

        message = self._socket.takeNextMessage()

        if message.getTypeName() not in self._message_handlers:
            Logger.log("e", "No handler defined for message of type %s", message.getTypeName())
            return

        self._message_handlers[message.getTypeName()](message)

    def _onSocketError(self, error):
        """Private socket error handler"""

        if error.getErrorCode() == Arcus.ErrorCode.BindFailedError:
            self._port += 1
            Logger.log("d", "Socket was unable to bind to port, increasing port number to %s", self._port)
        elif error.getErrorCode() == Arcus.ErrorCode.ConnectionResetError:
            Logger.log("i", "Backend crashed or closed.")
        elif error.getErrorCode() == Arcus.ErrorCode.Debug:
            Logger.log("d", "Socket debug: %s", str(error))
            return
        else:
            Logger.log("w", "Unhandled socket error %s", str(error))

        self._createSocket()

    def _createSocket(self, protocol_file):
        """Creates a socket and attaches listeners."""

        if self._socket:
            Logger.log("d", "Previous socket existed. Closing that first.") # temp debug logging
            self._socket.stateChanged.disconnect(self._onSocketStateChanged)
            self._socket.messageReceived.disconnect(self._onMessageReceived)
            self._socket.error.disconnect(self._onSocketError)
            # Hack for (at least) Linux. If the socket is connecting, the close will deadlock.
            while self._socket.getState() == Arcus.SocketState.Opening:
                sleep(0.1)
            # If the error occurred due to parsing, both connections believe that connection is okay.
            # So we need to force a close.
            self._socket.close()

        self._socket = SignalSocket()
        self._socket.stateChanged.connect(self._onSocketStateChanged)
        self._socket.messageReceived.connect(self._onMessageReceived)
        self._socket.error.connect(self._onSocketError)

        if Platform.isWindows():
            # On Windows, the Protobuf DiskSourceTree does stupid things with paths.
            # So convert to forward slashes here so it finds the proto file properly.
            # Using sys.getfilesystemencoding() avoid the application crashing if it is
            # installed on a path with non-ascii characters GitHub issue #3907
            protocol_file = protocol_file.replace("\\", "/").encode(sys.getfilesystemencoding())

        if not self._socket.registerAllMessageTypes(protocol_file):
            Logger.log("e", "Could not register Uranium protocol messages: %s", self._socket.getLastError())

        if UM.Application.Application.getInstance().getUseExternalBackend():
            Logger.log("i", "Listening for backend connections on %s", self._port)

        self._socket.listen("127.0.0.1", self._port)
