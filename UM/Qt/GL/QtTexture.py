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

    def getTextureId(self):
        return self._qt_texture.textureId()

    def bind(self, unit):
        self._qt_texture.bind(unit)

    def release(self, unit):
        self._qt_texture.release(unit)

    def load(self, file_name):
        image = QImage(file_name).mirrored()
        self._qt_texture.setData(image)
