# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtGui import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

##  An interface for OpenGL FrameBuffer Objects.
#
#   This class describes a minimal interface that is expected of FrameBuffer Object
#   classes.
class FrameBufferObject:
    def __init__(self, width, height):
        super().__init__()

        buffer_format = QOpenGLFramebufferObjectFormat()
        buffer_format.setAttachment(QOpenGLFramebufferObject.Depth)
        self._fbo = QOpenGLFramebufferObject(width, height, buffer_format)

        self._contents = None

    ##  Get the texture ID of the texture target of this FBO.
    def getTextureId(self):
        return self._fbo.texture()

    ##  Bind the FBO so it can be rendered to.
    def bind(self):
        self._contents = None
        self._fbo.bind()

    ##  Release the FBO so it will no longer be rendered to.
    def release(self):
        self._fbo.release()

    ##  Get the contents of the FBO as an image data object.
    def getContents(self):
        if not self._contents:
            self._contents = self._fbo.toImage()

        return self._contents