from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
import struct
import time
class ScannerEngineBackend(Backend):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        time.sleep(2)
        self._socket_thread.sendCommand(1) # Debug stuff
        while True:
            self._socket_thread.recieve()
            reply = self._socket_thread.getNextReply()
           
            if reply.data is not None:
                print(self.convertBytesToVerticeWithNormalsList(reply.data))