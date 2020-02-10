# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtGui import QOpenGLTexture, QImage, QAbstractOpenGLFunctions


class Texture:
    """A class describing the interface to be used for texture objects.

    This interface should be implemented by OpenGL implementations to handle texture
    objects.
    """
    def __init__(self, open_gl_binding_object: QAbstractOpenGLFunctions) -> None:
        super().__init__()

        self._qt_texture = QOpenGLTexture(QOpenGLTexture.Target2D)
        self._gl = open_gl_binding_object
        self._file_name = None
        self._image = None

    def getTextureId(self) -> int:
        """Get the OpenGL ID of the texture."""
        return self._qt_texture.textureId()

    def bind(self, texture_unit):
        """Bind the texture to a certain texture unit.

        :param texture_unit: The texture unit to bind to.
        """
        if not self._qt_texture.isCreated():
            if self._file_name != None:
                self._image = QImage(self._file_name).mirrored()
            elif self._image is None: # No filename or image set.
                self._image = QImage(1, 1, QImage.Format_ARGB32)
                self._image.fill(0)
            self._qt_texture.setData(self._image)
            self._qt_texture.setMinMagFilters(QOpenGLTexture.Linear, QOpenGLTexture.Linear)

        self._qt_texture.bind(texture_unit)
    def release(self, texture_unit):
        """Release the texture from a certain texture unit.

        :param texture_unit: The texture unit to release from.
        """
        self._qt_texture.release(texture_unit)

    def load(self, file_name):
        """Load an image and upload it to the texture.

        :param file_name: The file name of the image to load.
        """
        self._file_name = file_name
        # Actually loading the texture is postponed until the next bind() call.
        # This makes sure we are on the right thread and have a current context when trying to upload.

    def setImage(self, image):
        self._image = image