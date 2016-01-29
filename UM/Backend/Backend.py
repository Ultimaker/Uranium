# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Backend.SignalSocket import SignalSocket
from UM.Preferences import Preferences
from UM.Logger import Logger
from UM.Signal import Signal, SignalEmitter
from UM.Application import Application
from UM.PluginObject import PluginObject

import Arcus

import struct
import subprocess
import threading
import platform
import sys
from time import sleep

##      Base class for any backend communication (seperate piece of software).
#       It makes use of the Socket class from libArcus for the actual communication bits.
#       The message_handler dict should be filled with message class, function pairs.
class Backend(PluginObject, SignalEmitter):
    def __init__(self):
        super().__init__() # Call super to make multiple inheritence work.
        self._supported_commands = {}

        self._message_handlers = {}

        self._socket = None
        self._port = 49674
        self._process = None
        self._backend_log = []

        Application.getInstance().callLater(self._createSocket)

    processingProgress = Signal()
    backendConnected = Signal()

    ##   \brief Start the backend / engine.
    #   Runs the engine, this is only called when the socket is fully opend & ready to accept connections
    def startEngine(self):
        try:
            command = self.getEngineCommand()
            if not command:
                self._createSocket()
                return

            self._backend_log = []
            self._process = self._runEngineProcess(command)
            Logger.log("i", "Started engine process: %s" % (self.getEngineCommand()[0]))
            self._backend_log.append(bytes("Calling engine with: %s\n" % self.getEngineCommand(), 'utf-8'))
            t = threading.Thread(target=self._storeOutputToLogThread, args=(self._process.stdout,))
            t.daemon = True
            t.start()
            t = threading.Thread(target=self._storeOutputToLogThread, args=(self._process.stderr,))
            t.daemon = True
            t.start()
        except FileNotFoundError as e:
            Logger.log("e", "Unable to find backend executable: %s" % (self.getEngineCommand()[0]))

    def close(self):
        if self._socket:
            self._socket.close()
    
    ##  Get the logging messages of the backend connection.
    #   \returns  
    def getLog(self):
        return self._backend_log

    ##  \brief Convert byte array containing 3 floats per vertex
    def convertBytesToVerticeList(self, data):
        result = []
        if not (len(data) % 12):
            if data is not None:
                for index in range(0,int(len(data)/12)): #For each 12 bits (3 floats)
                    result.append(struct.unpack("fff",data[index*12:index*12+12]))
                return result
        else:
            Logger.log("e", "Data length was incorrect for requested type")
            return None
    
    ##  \brief Convert byte array containing 6 floats per vertex
    def convertBytesToVerticeWithNormalsList(self,data):
        result = []
        if not (len(data) % 24):
            if data is not None:
                for index in range(0,int(len(data)/24)): #For each 24 bits (6 floats)
                    result.append(struct.unpack("ffffff",data[index*24:index*24+24]))
                return result
        else:
            Logger.log("e", "Data length was incorrect for requested type")
            return None
    
    ##  Get the command used to start the backend executable 
    def getEngineCommand(self):
        return [Preferences.getInstance().getValue("backend/location"), "--port", str(self._socket.getPort())]

    ##  Start the (external) backend process.
    def _runEngineProcess(self, command_list):
        kwargs = {}
        if sys.platform == "win32":
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = su
            kwargs["creationflags"] = 0x00004000 #BELOW_NORMAL_PRIORITY_CLASS
        return subprocess.Popen(command_list, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

    def _storeOutputToLogThread(self, handle):
        while True:
            line = handle.readline()
            if line == b"":
                break
            self._backend_log.append(line)

    ##  Private socket state changed handler.
    def _onSocketStateChanged(self, state):
        if state == Arcus.SocketState.Listening:
            if not Application.getInstance().getCommandLineOption("external-backend", False):
                self.startEngine()
        elif state == Arcus.SocketState.Connected:
            Logger.log("d", "Backend connected on port %s", self._port)
            self.backendConnected.emit()
    
    ##  Private message handler
    def _onMessageReceived(self):
        message = self._socket.takeNextMessage()

        if message.getTypeName() not in self._message_handlers:
            Logger.log("e", "No handler defined for message of type %s", type(message))
            return

        self._message_handlers[message.getTypeName()](message)
    
    ##  Private socket error handler   
    def _onSocketError(self, error):
        #Logger.log("d", str(error))

        if error.getErrorCode() == Arcus.ErrorCode.BindFailedError:
            self._port += 1
        elif error.getErrorCode() == Arcus.ErrorCode.ConnectionResetError:
            Logger.log("i", "Backend crashed or closed. Restarting...")
        else:
            Logger.log("w", str(error))

        self._createSocket()
    
    ##  Creates a socket and attaches listeners.
    def _createSocket(self, protocol_file):
        if self._socket:
            self._socket.stateChanged.disconnect(self._onSocketStateChanged)
            self._socket.messageReceived.disconnect(self._onMessageReceived)
            self._socket.error.disconnect(self._onSocketError)

        self._socket = SignalSocket()
        self._socket.stateChanged.connect(self._onSocketStateChanged)
        self._socket.messageReceived.connect(self._onMessageReceived)
        self._socket.error.connect(self._onSocketError)

        if not self._socket.registerAllMessageTypes(protocol_file):
            Logger.log("e", "Could not register Cura protocol messages: %s", self._socket.getLastError())

        if Application.getInstance().getCommandLineOption("external-backend", False):
            Logger.log("i", "Listening for backend connections on %s", self._port)

        self._socket.listen("127.0.0.1", self._port)

