# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtGui import QImage
from PyQt6.QtOpenGL import QOpenGLTexture, QAbstractOpenGLFunctions

from UM.Logger import Logger

class Texture:
    """A class describing the interface to be used for texture objects.

    This interface should be implemented by OpenGL implementations to handle texture
    objects.
    """
    def __init__(self, open_gl_binding_object: QAbstractOpenGLFunctions, fallback_width: int = 1, fallback_height: int = 1) -> None:
        super().__init__()

        self._qt_texture = QOpenGLTexture(QOpenGLTexture.Target.Target2D)
        self._gl = open_gl_binding_object
        self._file_name = None
        self._image = None
        self._fallback_width = fallback_width
        self._fallback_height = fallback_height
        self._pixel_updates = []

    def getTextureId(self) -> int:
        """Get the OpenGL ID of the texture."""
        return self._qt_texture.textureId()

    def _performPixelUpdates(self) -> None:
        if self._image is None:
            Logger.warning("Attempt to update OpenGL texture pixels without an image set.")
            return
        xrange = range(self._image.width())
        yrange = range(self._image.height())
        for (xx, yy, color) in self._pixel_updates:
            x = int(xx * xrange.stop)
            y = int(yy * yrange.stop)
            if not (x in xrange and y in yrange):
                Logger.warning(f"Attempt to set pixel <{x}, {y}> to OpenGL texture outside of image bounds [{xrange.stop}x{yrange.stop}].")
                continue
            self._qt_texture.setData(x, y, 0, 1, 1, 1, QOpenGLTexture.PixelFormat.RGBA, QOpenGLTexture.PixelType.UInt8, bytes(color))
        self._pixel_updates.clear()

    def bind(self, texture_unit):
        """Bind the texture to a certain texture unit.

        :param texture_unit: The texture unit to bind to.
        """
        if not self._qt_texture.isCreated():
            if self._file_name != None:
                self._image = QImage(self._file_name).mirrored()
            elif self._image is None: # No filename or image set.
                self._image = QImage(self._fallback_width, self._fallback_height, QImage.Format.Format_ARGB32)
                self._image.fill(0)
            self._qt_texture.setData(self._image)
            self._qt_texture.setMinMagFilters(QOpenGLTexture.Filter.Linear, QOpenGLTexture.Filter.Linear)
        self._performPixelUpdates()
        self._qt_texture.bind(texture_unit)

    def setPixel(self, x: float, y: float, color: [int]) -> None:
        """ Put a new pixel into the texture (activates on next `bind` call).

        :param x: Horizontal position of pixel to set.
        :param y: Vertical position of pixel to set.
        :param color: Array with four uint8 bytes `[R8, G8, B8, A8]`.
        """
        self._pixel_updates.append((x, y, color))

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
