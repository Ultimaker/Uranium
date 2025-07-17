# Copyright (c) 2025 UltiMaker
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import List, Optional, Tuple

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtOpenGL import QOpenGLTexture, QAbstractOpenGLFunctions

from UM.Logger import Logger


class Texture:
    """A class describing the interface to be used for texture objects.

    This interface should be implemented by OpenGL implementations to handle texture
    objects.
    """
    def __init__(self, open_gl_binding_object: QAbstractOpenGLFunctions, fallback_width: int = 1, fallback_height: int = 1, aa_filter: QOpenGLTexture.Filter = QOpenGLTexture.Filter.Nearest) -> None:
        super().__init__()

        self._qt_texture = QOpenGLTexture(QOpenGLTexture.Target.Target2D)
        self._gl = open_gl_binding_object
        self._file_name = None
        self._image = None
        self._fallback_width = fallback_width
        self._fallback_height = fallback_height
        self._aa_filter = aa_filter
        self._subimage_updates: List[Tuple[QImage, int, int, QImage]] = []

    def getTextureId(self) -> int:
        """Get the OpenGL ID of the texture."""
        return self._qt_texture.textureId()

    def getWidth(self) -> int:
        return self._image.width() if self._image is not None else self._fallback_width

    def getHeight(self) -> int:
        return self._image.height() if self._image is not None else self._fallback_height

    def getImage(self) -> QImage:
        return self._image

    def _performSubImageUpdates(self) -> None:
        if self._image is None:
            Logger.warning("Attempt to update OpenGL texture pixels without an image set.")
            return
        for (updated, x, y, image) in self._subimage_updates:
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.drawImage(0, 0, updated)
            painter.end()
            self._qt_texture.setData(x, y, 0, image.width(), image.height(), 1, QOpenGLTexture.PixelFormat.BGRA, QOpenGLTexture.PixelType.UInt8, image.bits())
        self._subimage_updates.clear()

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
            self._qt_texture.setMinMagFilters(self._aa_filter, self._aa_filter)
        self._performSubImageUpdates()
        self._qt_texture.bind(texture_unit)

    def setSubImage(self, image: QImage, x: int, y: int) -> Optional[QImage]:
        if not (0 <= x <= self._image.width() - image.width() and 0 <= y <= self._image.height() - image.height()):
            Logger.warning(f"Attempt to set image at <{x}, {y}> with dimensions <{image.width()},{image.height()}> to OpenGL texture would result in data outside of image bounds [{self._image.width()}x{self._image.height()}].")
        old_pixels = self._image.copy(QRect(x, y, image.width(), image.height()))
        painter = QPainter(self._image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawImage(x, y, image)
        painter.end()
        self._subimage_updates.append((image, x, y, old_pixels))
        return old_pixels

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

    def __deepcopy__(self, memo) -> "Texture":
        copied_texture = Texture(self._gl, self._fallback_width, self._fallback_height, self._aa_filter)
        copied_texture.setImage(QImage(self._image))
        return copied_texture
