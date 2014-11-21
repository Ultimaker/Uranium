from OpenGL.GL import *

##  A wrapper around an OpenGL buffer object.
#   Note that the actual OpenGL buffer object is not created until create() is called.
class Buffer(object):
    ##  Initialize.
    #   \param type The type of buffer this object represents. Should be one of the GL constants for buffer type.
    #   \param usage The usage hint passed to OpenGL for this buffer. Should be one of the GL constants for buffer usage.
    def __init__(self, type, usage):
        super(Buffer, self).__init__()
        self._buffer = 0
        self._type = type
        self._usage = usage

    ##  Create the actual buffer object.
    #   \param data The data to use for the buffer. Can be None. Should be a type supported by PyOpenGL, like a numpy array.
    def create(self, data = None):
        self._buffer = glGenBuffers(1)
        if data != None:
            self.setData(data)

    ##  Set the data of this buffer.
    #   \param data The data to use for the buffer. Should be a type supported by PyOpenGL, like a numpy array.
    def setData(self, data):
        self.bind()
        glBufferData(self._type, data.size * 4, data, self._usage)
        self.release()

    ##  Destroy the buffer object.
    def destroy(self):
        glDeleteBuffers(self._buffer)

    ##  Bind the buffer object so it can be used during rendering.
    def bind(self):
        glBindBuffer(self._type, self._buffer)

    ##  Release the buffer object.
    def release(self):
        glBindBuffer(self._type, 0)
