from UM.Backend.Backend import Backend
from UM.Preferences import Preferences
import time
class ScannerEngineBackend(Backend):
    def __init__(self):
        super(ScannerEngineBackend,self).__init__()
        time.sleep(2)
        self._socket_thread.sendCommand(9)
        self._socket_thread.sendCommand(9)