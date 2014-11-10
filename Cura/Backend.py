class Backend(object):
    __init__(self):
        self._supported_commands = {}
        self._socket = None
        
    def getSupportedCommands(self):
        return self._supported_commands
    
    def addSupportedCommand(self,command):
        pass