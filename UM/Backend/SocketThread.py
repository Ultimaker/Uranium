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
        self._server_socket = None
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
        
    def sendCommand(self,command_id, data = None):
        packed_command = struct.pack('@i', int(command_id))
        if data is not None:
            packed_command += struct.pack('@i',data)
        self._command_queue.put(ClientCommand(ClientCommand.SEND, packed_command))
    
    ##  Return the next command_id & data that was recieved
    def getNextCommand(self):
        command_data = self._command_queue.get()
        return command_data.command_id , command_data.data
    
    def run(self):
        while self.alive.isSet():
            try:
                # Queue.get with timeout to allow checking self.alive
                command = self._command_queue.get(True, 0.1)
                self.handlers[command.type](command)
            except queue.Empty as e:
                continue
    
    def join(self, timeout = None):
        self.alive.clear()
        threading.Thread.join(self, timeout)
    
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
 
    
    def _handle_CLOSE(self, cmd):
        self._data_socket.close()
        reply = ClientReply(ClientReply.SUCCESS)
        self._reply_queue.put(reply)
    
    def _handle_SEND(self, cmd):
        try:
            self._data_socket.sendall(struct.pack('@i', len(cmd.data)))
            self._data_socket.sendall(cmd.data)
            self._reply_queue.put(self._success_reply())
        except IOError as e:
            print(e)
            self._reply_queue.put(self._error_reply(str(e)))
    
    def _handle_RECEIVE(self, cmd):
        try:
            message_length = self._recieveInt32()
            data = self._recieve_n_bytes(message_length)
            if len(data) == message_length:
                self._reply_queue.put(self._success_reply(data))
                return
            
            self._reply_queue.put(self._error_reply('Socket closed prematurely'))     
        except IOError as e:
            self._reply_queue.put(self._error_reply(str(e)))
    
    def _recv_n_bytes(self, n):
        data = b''
        while len(data) < size:
            if self._data_socket is None:
                #Raise an IO error to signal the socket is closed.
                raise IOError() 
            recieved = self._socket.recv(size - len(data))
            data += recieved
            if len(recieved) <= 0:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
        return data
    
    def _recieveInt32(self):
        return struct.unpack('@i', self._recv_n_bytes(4))[0]
    
    def _error_reply(self, errstr):
        return ClientReply(ClientReply.ERROR, errstr)
    
    def _success_reply(self, data=None):
        return ClientReply(ClientReply.SUCCESS, data)