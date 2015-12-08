# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

from UM.View.GL.FrameBufferObject import FrameBufferObject

##  FrameBufferObject subclass using the PyQt OpenGL implementation.
class QtFrameBufferObject(FrameBufferObject):
    def __init__(self, width, height):
        super().__init__()

        buffer_format = QOpenGLFramebufferObjectFormat()
        buffer_format.setAttachment(QOpenGLFramebufferObject.Depth)
        self._fbo = QOpenGLFramebufferObject(width, height, buffer_format)

        self._contents = None

    def bind(self):
        self._contents = None
        self._fbo.bind()

    def release(self):
        self._fbo.release()

    def getTextureId(self):
        return self._fbo.texture()

    def getContents(self):
        if not self._contents:
            self._contents = self._fbo.toImage()

        return self._contents
