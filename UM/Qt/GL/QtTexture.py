# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QOpenGLTexture, QImage

from UM.View.GL.Texture import Texture
from UM.View.GL.OpenGL import OpenGL

##  Texture subclass using PyQt for the OpenGL implementation.
class QtTexture(Texture):
    def __init__(self):
        super().__init__()

        self._qt_texture = QOpenGLTexture(QOpenGLTexture.Target2D)
        self._gl = OpenGL.getInstance().getBindingsObject()
        self._file_name = None
        self._image = None

    def getTextureId(self):
        return self._qt_texture.textureId()

    def bind(self, unit):
        if not self._qt_texture.isCreated():
            if self._file_name != None:
                self._image = QImage(self._file_name).mirrored()
            elif self._image is None: # No filename or image set.
                self._image = QImage(1, 1, QImage.Format_ARGB32)
            self._qt_texture.setData(self._image)
            self._qt_texture.setMinMagFilters(QOpenGLTexture.Linear, QOpenGLTexture.Linear)

        self._qt_texture.bind(unit)

    def release(self, unit):
        self._qt_texture.release(unit)

    def setImage(self, image):
        self._image = image

    def load(self, file_name):
        self._file_name = file_name
        #Actually loading the texture is postponed until the next bind() call.
        #This makes sure we are on the right thread and have a current context when trying to upload.
