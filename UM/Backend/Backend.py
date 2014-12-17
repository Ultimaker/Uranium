from UM.Backend.CommandFactory import CommandFactory
from UM.Backend.SocketThread import SocketThread
from UM.Preferences import Preferences
import subprocess
from time import sleep

##      Base class for any backend communication (seperate piece of software).

class Backend(object):
    def __init__(self,):
        super(Backend, self).__init__() # Call super to make multiple inheritence work.
        self._supported_commands = {}
        self._command_factory = CommandFactory()
        
        self._socket_thread = SocketThread()
        self._socket_thread.start()
       
        self._socket_thread.connectTo('127.0.0.1' , 0xC20A)
        sleep(1) #Wait a bit until engine is running properly
        self._process = self._runEngineProcess([Preferences.getPreference("BackendLocation"), '--port', str(self._socket_thread.getPort())])
        #self._socket_thread.command_queue.put(ClientCommand(ClientCommand.CONNECT, ('localhost', 0xC20A)))
        
        
    ##  Get a list of supported commands of this backend instance.
    #   \returns List of Command objects
    def getSupportedCommands(self):
        return self._supported_commands
    
    ##  Add a command to be supported
    #   \param command The Command to be supported
    def addSupportedCommand(self,command):
        pass
    
    def recievedRawCommand(self,command_id, data):
        self._command_factory.create(command_id,data).run()
        
    def _runEngineProcess(self, command_list):
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
            kwargs['creationflags'] = 0x00004000 #BELOW_NORMAL_PRIORITY_CLASS
        return subprocess.Popen(command_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)