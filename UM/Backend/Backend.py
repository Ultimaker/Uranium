from UM.Backend.SignalSocket import SignalSocket
from UM.Preferences import Preferences
from UM.Logger import Logger
from UM.Signal import Signal, SignalEmitter
from UM.Application import Application
from UM.PluginObject import PluginObject

import struct
import subprocess
import threading
from time import sleep


##      Base class for any backend communication (seperate piece of software).
#       It makes use of the Socket class from libArcus for the actual communication bits.
#       The message_handler dict should be filled with message class, function pairs.
class Backend(PluginObject, SignalEmitter):
    def __init__(self,):
        super().__init__() # Call super to make multiple inheritence work.
        self._supported_commands = {}

        self._message_handlers = {}

        self._socket = None
        self._port = 49674
        self._createSocket()
        self._process = None
        self._backend_log = []

    processingProgress = Signal()
    backendConnected = Signal()

    ##   \brief Start the backend / engine.
    #   Runs the engine, this is only called when the socket is fully opend & ready to accept connections
    def startEngine(self):
        try:
            self._backend_log = []
            self._process = self._runEngineProcess(self.getEngineCommand())
            t = threading.Thread(target=self._storeOutputToLogThread, args=(self._process.stdout,))
            t.daemon = True
            t.start()
            t = threading.Thread(target=self._storeOutputToLogThread, args=(self._process.stderr,))
            t.daemon = True
            t.start()
        except FileNotFoundError as e:
            Logger.log('e', "Unable to find backend executable")

    def close(self):
        if self._socket:
            self._socket.close()

    def getLog(self):
        return self._backend_log

    ##  \brief Convert byte array containing 3 floats per vertex
    def convertBytesToVerticeList(self, data):
        result = []
        if not (len(data) % 12):
            if data is not None:
                for index in range(0,int(len(data)/12)): #For each 12 bits (3 floats)
                    result.append(struct.unpack('fff',data[index*12:index*12+12]))
                return result
        else:
            Logger.log('e', "Data length was incorrect for requested type")
            return None
    
    ##  \brief Convert byte array containing 6 floats per vertex
    def convertBytesToVerticeWithNormalsList(self,data):
        result = []
        if not (len(data) % 24):
            if data is not None:
                for index in range(0,int(len(data)/24)): #For each 24 bits (6 floats)
                    result.append(struct.unpack('ffffff',data[index*24:index*24+24]))
                return result
        else:
            Logger.log('e', "Data length was incorrect for requested type")
            return None

    def getEngineCommand(self):
        return [Preferences.getPreference("BackendLocation"), '--port', str(self._socket_thread.getPort())]

    ## \brief Start the (external) backend process.
    def _runEngineProcess(self, command_list):
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
            kwargs['creationflags'] = 0x00004000 #BELOW_NORMAL_PRIORITY_CLASS
        return subprocess.Popen(command_list, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

    def _storeOutputToLogThread(self, handle):
        while True:
            line = handle.readline()
            if line == '':
                break
            self._backend_log.append(line)

    def _onSocketStateChanged(self, state):
        if state == SignalSocket.ListeningState:
            if not Application.getInstance().getArgument('external-backend', False):
                self.startEngine()
        elif state == SignalSocket.ConnectedState:
            Logger.log('d', "Backend connected on port %s", self._port)
            self.backendConnected.emit()

    def _onMessageReceived(self):
        message = self._socket.takeNextMessage()

        if type(message) not in self._message_handlers:
            Logger.log('e', "No handler defined for message of type %s", type(message))
            return

        self._message_handlers[type(message)](message)

    def _onSocketError(self, error):
        if error.errno == 98:
            self._port += 1
            self._createSocket()
        elif error.errno == 104 or error.errno == 32:
            Logger.log('i', "Backend crashed or closed. Restarting...")
            self._createSocket()
        elif error.winerror == 154:
            Logger.log('i', "Backend crashed or closed. Restarting...")
            self._createSocket()
        else:
            Logger.log('e', str(error))

    def _createSocket(self):
        if self._socket:
            self._socket.stateChanged.disconnect(self._onSocketStateChanged)
            self._socket.messageReceived.disconnect(self._onMessageReceived)
            self._socket.error.disconnect(self._onSocketError)

        self._socket = SignalSocket()
        self._socket.stateChanged.connect(self._onSocketStateChanged)
        self._socket.messageReceived.connect(self._onMessageReceived)
        self._socket.error.connect(self._onSocketError)

        self._socket.listen('127.0.0.1', self._port)

