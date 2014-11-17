class Socket(object):
    def __init__(self):
        super(Socket, self).__init__() # Call super to make multiple inheritence work.
        is_connected = False
    
    def initConnection(self, ip, port):
        pass
    
    def closeConnection(self):
        pass