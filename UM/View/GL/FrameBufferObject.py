# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtGui import QImage, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat


class FrameBufferObject:
    """An interface for OpenGL FrameBuffer Objects.

    This class describes a minimal interface that is expected of FrameBuffer Object
    classes.
    """
    def __init__(self, width: int, height: int) -> None:
        super().__init__()

        buffer_format = QOpenGLFramebufferObjectFormat()
        buffer_format.setAttachment(QOpenGLFramebufferObject.Depth)
        self._fbo = QOpenGLFramebufferObject(width, height, buffer_format)

        self._contents = None

    def getTextureId(self) -> int:
        """Get the texture ID of the texture target of this FBO."""
        return self._fbo.texture()

    def bind(self) -> None:
        """Bind the FBO so it can be rendered to."""
        self._contents = None
        self._fbo.bind()

    def release(self) -> None:
        """Release the FBO so it will no longer be rendered to."""
        self._fbo.release()

    def getContents(self) -> QImage:
        """Get the contents of the FBO as an image data object."""
        if not self._contents:
            self._contents = self._fbo.toImage()

        return self._contents