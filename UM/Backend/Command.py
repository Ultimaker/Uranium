class Command(object):
    def __init__(self, socket):
        super(Command, self).__init__() # Call super to make multiple inheritence work.
        self._data = None
        self._id = 0
        self._socket = socket
        
    def setData(self, data):
        self._data = data
        
    def getData(self):
        return self._data
    
    def getID(self):
        return self._id
        
    def send(self):
        raise NotImplementedError("Command is not correctly implemented. It needs a send")
    
    def recieve(self):
        raise NotImplementedError("Command is not correctly implemented. It needs a recieve")
    
    def serialize(self, socket):
        pass
    
    def deserialize(self, socket):
        pass
    