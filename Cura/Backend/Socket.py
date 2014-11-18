class Socket(object):
    def __init__(self,backend, server_port=0xC20A):
        super(Socket, self).__init__() # Call super to make multiple inheritence work.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_port = server_port
        while True:
            try:
                self._socket.bind(('127.0.0.1', self._server_port))
            except:
                print("Failed to listen on port: %d" % (self._server_port))
                self._self._server_port += 1
                if self._self._server_port > 0xFFFF:
                    print("Failed to listen on any port...") #TODO; add Logging
                    break
            else:
                break
        
        self._thread = None
        self._data_socket = None
        self._listen_thread = threading.Thread(target=self._socketListenFunction)
        self._listen_thread.daemon = True
        self._listen_thread.start()
        self._backend = backend
    
    def _socketListenFunction(self):
        self._socket.listen(1)
        print('Listening for engine communications on %d' % (self._server_port)) #TODO; add logging
        while True:
            try:
                self._data_socket, _ = self._socket.accept()
                self._thread = threading.Thread(target = self._socketConnectFunction)
                self._thread.daemon = True
                self._thread.start()
            except socket.error as e:
                if e.errno != errno.EINTR:
                    raise
    
    def recievedRawCommand(self, command_id, data):
        backend.recievedRawCommand(command_id, data)
    
    def _socketConnectFunction(self):
        try:
            while self._data_socket is not None:
                command = self.readInt32()
                size = self.readInt32()
                data = self.read(size)
                self.received(command, data)
        except IOError:
            pass
        self._close()
   
    ##   If current connection is open, close it. 
    def _close(self):
        if self._dataSocket is not None:
            try:
                self._dataSocket.close()
            except:
                pass
            self._dataSocket = None

    def readInt32(self):
        return struct.unpack('@i', self.read(4))[0]

    def read(self, size):
        data = ''
        while len(data) < size:
            if self._data_socket is None:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
            recv = self._data_socket.recv(size - len(data))
            data += recv
            if len(recv) <= 0:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
        return data

    def sendData(self, command_id, data):
        if self._data_socket is None:
            return False
        self._data_socket.sendall(struct.pack('@i', command_id))
        if data is not None:
            self._data_socket.sendall(struct.pack('@i', len(data)))
            self._data_socket.sendall(data)
        else:
            self._data_socket.sendall(struct.pack('@i', 0))
        return True