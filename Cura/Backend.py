class Backend(object):
    def __init__(self):
        super(Backend, self).__init__()
        self._supported_commands = {}
        self._socket = None
        
    def getSupportedCommands(self):
        return self._supported_commands
    
    def addSupportedCommand(self,command):
        pass