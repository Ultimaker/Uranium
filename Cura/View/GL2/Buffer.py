from OpenGL.GL import *

class Buffer(object):
    def __init__(self, type, usage):
        super(Buffer, self).__init__()
        self._buffer = 0
        self._type = type
        self._usage = usage

    def create(self, data = None):
        self._buffer = glGenBuffers(1)
        if data:
            self.setData(data)

    def setData(self, data):
        self.bind()
        glBufferData(self._type, len(data), data, self._usage)
        self.release()

    def destroy(self):
        glDeleteBuffers(self._buffer)

    def bind(self):
        glBindBuffer(self._type, self._buffer)

    def release(self):
        glBindBuffer(self._type, 0)
