from UM.Backend.CommandFactory import CommandFactory
from UM.Backend.SocketThread import SocketThread
from UM.Preferences import Preferences
from UM.Logger import Logger
import struct
import subprocess
from time import sleep
from UM.Backend.SocketThread import ClientReply

##      Base class for any backend communication (seperate piece of software).
#       It uses the command_handlers to know what to do with each command. 
#       The command_handler dict should be filled with id, function pairs (where the function requres a byte stream to be passed to it)
#       The ID is formed by the first 4 bits of the message. 
class Backend(object):
    def __init__(self,):
        super(Backend, self).__init__() # Call super to make multiple inheritence work.
        self._supported_commands = {}
        self._command_factory = CommandFactory()
        
        self._socket_thread = SocketThread()
        self._socket_thread.start()
       
        self._socket_thread.connectTo('127.0.0.1' , 0xC20A)
        self._command_handlers = {}
        self._socket_thread.socketOpen.connect(self.startEngine)
        self._socket_thread.replyAdded.connect(self.handleNextReply)

        self._process = None
    
    
    ##   \brief Start the backend / engine. 
    #   Runs the engine, this is only called when the socket is fully opend & ready to accept connections
    def startEngine(self):
        try:
            self._process = self._runEngineProcess(self.getEngineCommand())
        except FileNotFoundError as e:
            Logger.log('e', "Unable to find backend executable")
    
    ##   Parse the next reply and handle it (based on command_handlers)
    def handleNextReply(self):
        self.interpretData(self.recieveData())
    
    ##  Interpret a byte stream as a command. 
    #   Based on the command_id (the fist 4 bits of the message) a different action will be taken.
    #   \param data byte stream to interpret
    #   \returns None if command was not recognised, result of command if it was (can still be None!)
    def interpretData(self, data):
        data_id = struct.unpack('i', data[0:4])[0]
        if data_id in self._command_handlers:
            return self._command_handlers[data_id](data[4:len(data)])
        else:
            Logger.log('e', "Command type %s not recognised" % (data_id))
            return None
    
    ##  \brief Recieve a single package of data (this should be a 'full' command)
    def recieveData(self):
        while True:
            reply = self._socket_thread.getNextReply()
            if reply.type is ClientReply.SUCCESS:
                if reply.data is not None:
                    return reply.data
            if reply.type is ClientReply.ERROR:
                print("An error occured with connection with message: " + str(reply.data))
                return None
    
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
        return subprocess.Popen(command_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
