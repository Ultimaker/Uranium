import struct
import threading
import queue
import socket

# server_port=0xC20A

class ClientCommand(object):
    """ A command to the client thread.
    Each command type has its associated data:
    CONNECT: (host, port) tuple
    SEND: Data string
    RECEIVE: None
    CLOSE: None
    """
    CONNECT, SEND, RECEIVE, CLOSE = range(4)
    def __init__(self, type, data = None):
        self.type = type
        self.data = data
        
class ClientReply(object):
    """ A reply from the client thread.
    Each reply type has its associated data:
    ERROR: The error string
    SUCCESS: Depends on the command - for RECEIVE it's the received
    data string, for others None.
    """
    ERROR, SUCCESS = range(2)
    def __init__(self, type, data=None):
        self.type = type
        self.data = data

# The socket thread acts as a server. 

class SocketThread(threading.Thread):
    def __init__(self, command_queue=queue.Queue(), reply_queue=queue.Queue()):
        super(SocketThread, self).__init__()
        self._command_queue = command_queue
        self._reply_queue = reply_queue
        self.alive = threading.Event()
        self.alive.set()
        self._host = '127.0.0.1'
        self._port = None
        
        ## The server socket is where the GUI is listening for connections from the backend.
        self._server_socket = None
        
        ## Socket created when the engine connects. As we only have one backend, we only need one data socket.
        self._data_socket = None
        self.handlers = {
            ClientCommand.CONNECT: self._handle_CONNECT,
            ClientCommand.CLOSE: self._handle_CLOSE,
            ClientCommand.SEND: self._handle_SEND,
            ClientCommand.RECEIVE: self._handle_RECEIVE,
        }
    
   
    def getPort(self):
        return self._port
    
    def connectTo(self, host, port):
        self._command_queue.put(ClientCommand(ClientCommand.CONNECT, (port)))
    
    ## Get the latest reply.
    def getNextReply(self):
        return self._reply_queue.get(True)
    
    ## \brief Start listening for communication 'package'
    #   This will start listening for the next burst of communication.
    #   It pushes a ClientReply to the response queue. The type of this
    #   command indicates if it was succesfull or not. Use getNextReply to
    #   obtain the next reply
    def recieve(self):
        self._command_queue.put(ClientCommand(ClientCommand.RECEIVE))
        
    def sendCommand(self,command_id, data = None):
        packed_command = struct.pack('@i', int(command_id))
        if data is not None:
            packed_command += struct.pack('@i',data)
        self._command_queue.put(ClientCommand(ClientCommand.SEND, packed_command))
    
    def run(self):
        while self.alive.isSet():
            try:
                # Queue.get with timeout to allow checking self.alive
                command = self._command_queue.get(True, 0.1)
                self.handlers[command.type](command)
            except queue.Empty as e:
                continue
    
    ## Try to join the thread.
    # \param timeout The timeout for the join operation
    def join(self, timeout = None):
        self.alive.clear()
        threading.Thread.join(self, timeout)
    
    ##  Function that is executed if a connect command is sent.
    def _handle_CONNECT(self, cmd):
        self._host = "127.0.0.1"
        self._port = 49674 #Hardcoded stuff
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self._server_socket.bind(('', self._port))
            except:
                self._port += 1
                if self._port > 0xFFFF:
                    break
            else:
                break
        print("Listening for backend on " + str(self._port))
        self._server_socket.listen(1)
        
        self._data_socket, address = self._server_socket.accept()
        print("Backend connected on " + str(address))
 
    ##  Function that is executed if a close command is sent.
    def _handle_CLOSE(self, cmd):
        self._data_socket.close()
        reply = ClientReply(ClientReply.SUCCESS)
        self._reply_queue.put(reply)
    
    ##  Function that is executed if a send command is sent.
    def _handle_SEND(self, cmd):
        try:
            self._data_socket.sendall(struct.pack('@i', len(cmd.data)))
            self._data_socket.sendall(cmd.data)
            self._reply_queue.put(self._createSuccessReply())
        except IOError as e:
            print(e)
            self._reply_queue.put(self._createErrorReply(str(e)))
    
    ##  Function that is executed if a recieve command is sent.
    def _handle_RECEIVE(self, cmd):
        try:
            message_length = self._recieveInt32()
            data = self._recieve_n_bytes(message_length)
            if len(data) == message_length:
                self._reply_queue.put(self._createSuccessReply(data))
                return
            self._reply_queue.put(self._createErrorReply('Socket closed prematurely'))     
        except IOError as e:
            self._reply_queue.put(self._createErrorReply(str(e)))
    
    ##  Recieve a certain number of bytes.
    #   \param size Number of bytes to recieve
    #   \return data byte array (packed).
    #   \throws IOError When socket has been closed.
    def _recieve_n_bytes(self, size):
        data = b''
        while len(data) < size:
            if self._data_socket is None:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
            recieved = self._data_socket.recv(size - len(data))
            data += recieved
            if len(recieved) <= 0:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
        return data
    
    def _recieveInt32(self):
        return struct.unpack('@i', self._recieve_n_bytes(4))[0]
    
    ##  Convenience function to create error reply
    def _createErrorReply(self, errstr):
        return ClientReply(ClientReply.ERROR, errstr)
    ##  Convenience function to create succes reply
    def _createSuccessReply(self, data=None):
        return ClientReply(ClientReply.SUCCESS, data)